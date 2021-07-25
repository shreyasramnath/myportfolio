import json
import boto3
import io
import zipfile
def lambda_handler(event, context):
    sns = boto3.resource('sns')
    s3 = boto3.resource('s3')
    try:
        portfolio_bucket = s3.Bucket('portfolio.shreyasramnath.com')
        build_bucket = s3.Bucket('portfoliobuild.shreyasramnath.com')
        build_bucket.download_file('portfoliobuild.zip', '/tmp/portfoliobuild.zip')
        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm)
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        topic = sns.Topic('arn:aws:sns:us-east-1:048847678797:portfolioTopic')
        topic.publish(Subject='Test', Message='k')
    except: topic.publish(Subject='fail', Message='f')
    raise

