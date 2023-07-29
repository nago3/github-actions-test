import os
import sys
import logging
import pymysql
import json

# rds settings
RDS_HOST  = os.environ['RDS_HOST']
USER_NAME = os.environ['USER_NAME']
PASSWPRD = os.environ['PASSWPRD']
DB_NAME = os.environ['DB_NAME']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    DB:
        MySQL
    Table:
        users
    Column:
        id              int(11)      NOT NULL AUTO_INCREMENT,
        cognito_user_id varchar(255) NOT NULL,
        created_at      datetime     NOT NULL,
    """
    print(event)

    # 1. MySQL に接続する設定
    try:
        conn = pymysql.connect(
                   host=RDS_HOST,
                   user=USER_NAME,
                   passwd=PASSWPRD,
                   db=DB_NAME,
                   connect_timeout=5)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

    # 2. Cognito User ID を取得
    try:
        cognito_user_id = event['requestContext']['authorizer']['claims']['sub']
        print(cognito_user_id)
        logger.info("SUCCESS: CognitoUserID has been got from API")
    except Exception as e:
        print(e)
        logger.error("ERROR: CognitoUserID has not been got from API")
        sys.exit()

    # 3. MySQL に接続し、user_id を取得
    query__for_insert_user = """
        SELECT id FROM users WHERE cognito_user_id = %s
    """
    with conn.cursor() as cur:
        cur.execute(query__for_insert_user, (cognito_user_id,))
        (user_id,) = cur.fetchone()
        print("user_id: ",user_id)
        conn.close()
    logger.info("SUCCESS: UserID has been got from RDS")
    
    # 4. API のレスポンスを作成
    responseBody = {
        "user_id": user_id
    }
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(responseBody)
    }
    return response