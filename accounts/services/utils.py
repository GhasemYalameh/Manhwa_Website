import os

def user_avatar_upload_to(instance, file_name):
    """
    a function for getting user avatar paths 
    """
    user_uuid= instance.id
    return os.path.join('User', user_uuid, file_name)