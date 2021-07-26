import json
import boto3
import io
import zipfile
def lambda_handler(event, context):
    sns = boto3.resource('sns')
    s3 = boto3.resource('s3')
    pipeline = boto3.client('codepipeline')
    location = {
        "bucketName": "portfoliobuild.shreyasramnath.com",
        "objectKey": "portfoliobuild.zip"
    }
    try:
        job = event.get('CodePipeline.job');
        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "portfolio":
                    location = artifact["location"]["s3Location"]
                
        portfolio_bucket = s3.Bucket('portfolio.shreyasramnath.com')
        build_bucket = s3.Bucket(location["bucketName"])
        build_bucket.download_file('portfoliobuild.zip', '/tmp/portfoliobuild.zip')
        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm)
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        topic = sns.Topic('arn:aws:sns:us-east-1:048847678797:portfolioTopic')
        topic.publish(Subject='Success', Message='successful')
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
    except: 
            topic.publish(Subject='Fail', Message='failure')
            raise
    response = pipeline.put_job_success_result(
        jobId=event['CodePipeline.job']['id']
    )
    return response