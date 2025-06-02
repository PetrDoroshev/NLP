import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# Спасибо группе с английскими статьями
def mod_push_to_sss(save_info, s3, bucket_name):
    s3_prefix = None

    for now_key, now_value in save_info.items():
        try:
            if os.path.isfile(now_value):
                file_name = os.path.basename(now_value)
                s3_key = os.path.join(file_name).replace(os.sep, '/')
                s3.upload_file(now_value, bucket_name, s3_key)
                print(f"Файл загружен: {s3_key}")
    
            elif os.path.isdir(now_value):
                base_dir = os.path.normpath(now_value)
                for root, dirs, files in os.walk(base_dir):
                    for file in files:
                        local_file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(local_file_path, start=base_dir).replace(os.sep, '/')
                        s3_key = os.path.join(now_key, rel_path).replace(os.sep, '/')
                        s3.upload_file(local_file_path, bucket_name, s3_key)
                        # print(f"Загружено: {s3_key}")
                print(f"Директория {now_value} полностью загружена в бакет {bucket_name}")
    
            else:
                raise ValueError(f"Путь {now_value} не существует или не является файлом/директорией")
    
        except NoCredentialsError:
            print("Ошибка аутентификации: не предоставлены учетные данные")
            return False
        except ClientError as e:
            print(f"Ошибка при загрузке в S3: {e}")
            return False
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return False
