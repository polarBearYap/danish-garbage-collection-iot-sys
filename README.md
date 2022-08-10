# danish-garbage-collection-iot-sys

## Table of contents
- [Overview](#overview)
- [Architecture diagram](#architecture-diagram)
- [Contributors](#contributors)
- [File structure](#file-structure)
- [Technical contribution](#technical-contribution)

## Overview
<p align="justify">The garbage collection system is inefficient in Danish House Student Hostel (which is located in UTAR Kampar campus). Each garbage bin only picked up by employees once per week even though the bin is already full for a few days. Most students are forced to put the trash outside of the garbage bins since the  bins are always full. As a result, the area becomes a breeding ground for pests like cockroach and Aedes. Numerous maggots crawl around the bin, dead cockroaches can be found everywhere in the stairway, surgical masks get thrown outside of bin and flown away... This inevitably will cause health problems to the students.</p>

## Architecture diagram
<p align="justify">The main AWS services used are  AWS IoT Greengrass. Two Ubuntu VirtualBox VMs are set up to represent the edge device and one of the IoT garbage bin, respectively.</p>

![Architecture diagram of garbage collection IoT system](./picture/architecture-diagram.png)

## Project Demo


## Contributors
1. Yap Jheng Khin (Leader)
2. Gan Win Sian (Co-leader)
3. Cheow Yue Chen
4. Kesavan a/l Muniandy

## File structure 

| Directory | Description |
| --- | --- |
| aws-cli | Contain files that are used in aws cli commands |
| bulk_registration | Contain files that are used in bulk registration, should place in core device's VM |
| client_device | Contain files that are used to perform inference and publish fill level telemetry, should place in client device's VM |
| component_recipes | Contain recipes of the components that needed to be configured during deployment |
| core_device | Contain files that are used when installing Greengrass Core software, should place in core device's VM |
| logs | Contain sample log files of a successful Greengrass custom component's deployment |
| picture | Contain the architecture diagram of the IoT system |
| s3_artifacts | Contain files that should be upload to S3 bucket named danish-gcs-model-artifacts-bucket |
| s3_output_files | Contain sample files that are downloaded from the S3 bucket named danish-gcs-image-and-model-output-bucket |
| technical_manual | Contain the technical manual to implement the IoT system in the AWS cloud |

## Technical Contribution

The manual also contains developer guide on how to develop a custom Greengrass component from a local virtual machine.   
