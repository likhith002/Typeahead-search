import requests
import json
import os
from fastapi import HTTPException
from .word_counter_mr_job import WordCounter
from app.schemas.response import CustomException, BaseResponseModel
# from mrjob.runner import HDFSRunner
# from mrjob.compat import get_hadoop_fs

hdfs_url = "http://namenode:9870/webhdfs/v1"
rm_url = "http://resourcemanager:8088/ws/v1/cluster/apps"


async def check_if_file_already_exsists(file_path: str):
    endpoint = f"{hdfs_url}{file_path}?op=GETFILESTATUS&user.name=root"
    try:
        # Make a GET request to check if the file exists
        response = requests.get(endpoint)

        if response.status_code == 200:
            print("Text file already exsists")
            return True  # File exists
        elif response.status_code == 404:
            return False  # File does not exist
        else:
            print(f"Error checking file status: {response.text}")
            return False  # Assume file does not exist on unexpected status
    except Exception as e:
        CustomException(
            detail="Unable to fetch file Status",
            status=500,
            debug_mode=e if __debug__ else None,
        )


async def upload_file_to_hdfs(local_file_path) -> BaseResponseModel:
    # HDFS Namenode URL

    file_name = local_file_path.split("/")[-1]

    # HDFS directory where files will be uploaded
    hdfs_upload_dir = "/"
    upload_url = f"{hdfs_url}{hdfs_upload_dir}{file_name}?op=CREATE&user.name=root"

    # Open the file and send it to HDFS
    file = open(local_file_path, "r")

    response = requests.put(upload_url, data=file.read())
    # Check if the upload was successful
    if response.status_code != 201:
        raise CustomException(
            status=response.status_code,
            detail=response.text,
            title="Failed to upload file to HDFS",
        )
    else:
        return BaseResponseModel(detail=f"File {file_name} uploaded to HDFS")


async def create_new_application_hdfs() -> str:
    post_url = f"{rm_url}/new-application"
    try:
        response = requests.post(post_url)
        if response.status_code == 200:
            data = response.json()

            return data["application-id"]
        else:
            raise CustomException(
                detail="Failed to create an application",
                status=response.status_code,
                debug_mode=response.text if __debug__ else None,
            )

    except Exception as e:
        raise CustomException(
            detail="Failed to create an application",
            status=500,
            debug_mode=e if __debug__ else None,
        )


async def download_outputs_folder(
    local_download_path: str, hdfs_folder_path: str = "/output"
):
    # Ensure the folder path ends with a slash "/"

    # Construct the URL to list files in the HDFS folder
    list_files_url = f"{hdfs_url}{hdfs_folder_path}?op=LISTSTATUS"

    # Make a GET request to list files in the HDFS folder
    response = requests.get(list_files_url)
    if response.status_code == 200:
        # Parse the JSON response to get file statuses
        json_response = response.json()

        file_statuses = json_response.get("FileStatuses", {}).get("FileStatus", [])

        # Create local download directory if it does not exist
        os.makedirs(local_download_path, exist_ok=True)

        # Download each file in the folder
        for file_status in file_statuses:
            file_name = file_status["pathSuffix"]
            file_hdfs_path = f"{hdfs_folder_path}/{file_name}"
            download_url = f"{hdfs_url}{file_hdfs_path}?op=OPEN&noredirect=false"
            local_file_path = os.path.join(local_download_path, file_name)

            # Download the file
            download_response = requests.get(download_url, stream=True)
            if download_response.status_code == 200:
                with open(local_file_path, "wb") as local_file:
                    for chunk in download_response.iter_content(chunk_size=8192):
                        local_file.write(chunk)

                print(f"Downloaded: {file_name} to {local_file_path}")
            else:
                raise CustomException(
                    status=download_response.status_code, detail="Failed to fetch file"
                )

    else:
        raise CustomException(
            status=response.status_code, detail="Failed to get target folder"
        )


async def submit_mapreduce_job(job_data):
    # Submit MapReduce job to Hadoop cluster
    # Example job_data format: {"input_file": "file_path_in_hdfs", "output_dir": "output_directory_in_hdfs"}

    # Upload input file to HDFS

    input_file_path = job_data["input_file"]
    hdfs_file_path = "/" + input_file_path.split("/")[-1]
    is_file_present = await check_if_file_already_exsists(hdfs_file_path)
    if is_file_present is False:
        await upload_file_to_hdfs(input_file_path)

    # create an application
    application_id = await create_new_application_hdfs()

    #     # Define the Hadoop REST API endpoint
    hadoop_rest_api_url = f"{rm_url}?user.name=root"

    print(application_id)
    input_path = "/text.txt"
    output_path = "/output"
    hadoop_home = "/opt/hadoop-3.2.1"
    mapreduce_jar_path = (
        f"{hadoop_home}/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.2.1.jar"
    )

    job_config = {
        "application-id": application_id,
        "application-name": "word_count",
        "am-container-spec": {
            "commands": {
                "command": f"{hadoop_home}/bin/hadoop jar {mapreduce_jar_path} wordcount -D mapreduce.output.fileoutputformat.overwrite=true {input_path} {output_path}"
            },
            "memory": 1024,
            "vCores": 1,
        },
        "application-type": "MAPREDUCE",
        "keep-containers-across-application-attempts": "false",
        "max-app-attempts": 2,
        "priority": 0,
        "queue": "default",
        "timeout-seconds": 600,
        "unmanaged-AM": "false",
    }

    # Submit the job to the Hadoop cluster
    # print(json.dumps(job_config))
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        hadoop_rest_api_url, data=json.dumps(job_config), headers=headers
    )

    # Check if the job submission was successful
    if response.status_code == 202:
        return BaseResponseModel(detail="Job submitted successfully")
        # print(response.text)

    else:
        print("Failed to submit job. Status code:", response.status_code)
        print("Error message:", response.text)
