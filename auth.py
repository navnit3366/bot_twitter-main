import os

#-------------credenciais do twitter-----------------#
tt_bearer_token = os.getenv('TT_BEARER_TOKEN')
tt_consumer_api_key = os.getenv('TT_CONSUMER_API_KEY')
tt_consumer_api_pass = os.getenv('TT_CONSUMER_API_PASS')
tt_access_token = os.getenv('TT_ACCESS_TOKEN')
tt_access_token_secret = os.getenv('TT_ACCESS_TOKEN_SECRET')
#-------------credenciais do imgur-------------------#
img_client_id = os.getenv('IMG_CLIENT_ID')
img_client_secret = os.getenv('IMG_CLIENT_SECRET')
#-------------credenciais do mysql-------------------#
mysql_user = os.getenv('MYSQL_USER')
mysql_pass = os.getenv('MYSQL_PASS')
mysql_host = os.getenv('MYSQL_HOST')
mysql_port = os.getenv('MYSQL_PORT')