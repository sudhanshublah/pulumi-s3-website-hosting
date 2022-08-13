"""A Python Pulumi program"""

import pulumi
import os
import mimetypes
import pulumi_aws as aws_classic
import pulumi_aws_native as aws_native
import json


bucket = aws_native.s3.Bucket(
    "my-website",
    website_configuration=aws_native.s3.BucketWebsiteConfigurationArgs(
        index_document='index.html'
    ),
)


content_dir = "www"
for file in os.listdir(content_dir):
    filepath = os.path.join(content_dir, file)
    mime_types, _ = mimetypes.guess_type(filepath)
    obj = aws_classic.s3.BucketObject(
        file,
        bucket=bucket.id,
        source=pulumi.FileAsset(filepath),
        content_type=mime_types,
        opts=pulumi.ResourceOptions(parent=bucket)
    )

bucket_policy = aws_classic.s3.BucketPolicy(
    "my-bucket-policy",
    bucket=bucket.id,
    policy=bucket.arn.apply(
        lambda arn: json.dumps({
            "Version":"2012-10-17",
            "Statement":[{
                "Effect": "Allow",
                "Principal": "*",
                "Action": [
                    "s3:GetObject"
                ],
                "Resource":[
                    f"{arn}/*"
                ]
            }]
        })
    ),
    opts=pulumi.ResourceOptions(parent=bucket)
)


pulumi.export("bucket_name", bucket.bucket_name)
pulumi.export('website_url', bucket.website_url)
