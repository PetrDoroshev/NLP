import os
import boto3

def mod_save_images(bucket_name, images_path):
    all_images_folder = sorted(os.listdir(images_path))

    
    s3 = session.client('s3', endpoint_url='https://storage.yandexcloud.net')
    
    # s3.upload_file(local_file_path, bucket_name, object_name)
    
    for now_images in all_images_folder:
        print(f"Processing: {now_images}")
        s3.upload_file(f"./{images_path}/{now_images}/", bucket_name, now_images)


# Example usage
if __name__ == '__main__':
    BUCKET_NAME = 'your-bucket-name'
    FOLDER_NAME = 'path/to/your/folder'  # e.g., 'myfolder/' or 'parent/child/'
    
    create_s3_folder(BUCKET_NAME, FOLDER_NAME)
