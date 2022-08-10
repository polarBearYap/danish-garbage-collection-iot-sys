# Danish Garbage Collection IoT System

## Table of contents
- [Overview](#overview)
- [Architecture diagram](#architecture-diagram)
- [Project demo](#project-demo)
- [File structure](#file-structure)
- [Technical contribution](#technical-contribution)
- [Project contributors](#project-contributors)
- [Acknowledgement](#acknowledgement)
- [Potential improvement](#potential-improvement)

## Overview
<p align="justify">The garbage collection system is inefficient in Danish House Student Hostel (which is located in UTAR Kampar campus). Each garbage bin only picked up by employees once per week even though the bin is already full for a few days. Most students are forced to put the trash outside of the garbage bins since the  bins are always full. As a result, the area becomes a breeding ground for pests like cockroach and Aedes. Numerous maggots crawl around the bin, dead cockroaches can be found everywhere in the stairway, surgical masks get thrown outside of bin and flown away... This inevitably will cause health problems to the students.</p>

## Architecture diagram
<p align="justify">The main AWS services used are  AWS IoT Greengrass. Two Ubuntu VirtualBox VMs are set up to represent the edge device and one of the IoT garbage bin, respectively.</p>

> Click on the image to enlarge. 

![Architecture diagram of garbage collection IoT system](./picture/architecture-diagram.png)

## Project Demo

## File structure 

| Directory | Description |
| --- | --- |
| aws-cli | Contain files that are used in aws cli commands |
| bulk_registration | Contain files that are used in bulk registration, should place in core device's VM |
| client_device | Contain files that are used to perform inference and publish fill level telemetry, should place in client device's VM |
| component_recipes | Contain recipes of the components that needed to be configured during deployment |
| core_device | Contain files that are used when installing Greengrass Core software, should place in core device's VM |
| logs | Contain sample log files of a successful Greengrass custom component's deployment |
| pdf_documents | Contain the assignment report and the step-by-step guide to set up the system |
| picture | Contain the architecture diagram of the IoT system and some report screenshots |
| s3_artifacts | Contain files that should be upload to S3 bucket named danish-gcs-model-artifacts-bucket |
| s3_output_files | Contain sample files that are downloaded from the S3 bucket named danish-gcs-image-and-model-output-bucket |


## Technical Contribution

1. As shown in the image below, the manual contains developer guide on how to develop a custom Greengrass component from a local virtual machine.

<img alt="Developer guide on developing custom Greengrass component" src="./picture/manual-guide-1.png" width="500">

2. As shown in the image below, the manual also describes the best MQTT design patterns recommended by [AWS](https://docs.aws.amazon.com/whitepapers/latest/designing-mqtt-topics-aws-iot-core/designing-mqtt-topics-aws-iot-core.html). 

<img alt="Developer guide on the MQTT best practices" src="./picture/manual-guide-2.png" width="500">

## Project contributors
1. Yap Jheng Khin (Leader)
2. Gan Win Sian (Co-leader)
3. Cheow Yue Chen
4. Kesavan a/l Muniandy

## Acknowledgement
Special thanks to Dr Cheng for providing free online introductory AWS course and 50% discount on AWS foundational certificate. Also, I would like to thank Dr Ashvaany for patiently guiding the assignment.
1. Ts Dr Cheng Wai Khuen
2. Dr Ashvaany a/p Egambaram

## Potential improvement
1. Infrastructure as a code (IaaC): Use [Terraform](https://www.terraform.io/) and [Ansible](https://www.ansible.com/) to automate cloud deployment.
2. Containerize the application by [configuring the Greengrass component to run Docker container](https://docs.aws.amazon.com/greengrass/v2/developerguide/run-docker-container.html) to leverage the benefits of containers.
3. Kubernetes: Deploy a lighweight Kubernetes distribution like [K3s](https://k3s.io/) into the edge device and let the Kubernetes controllers automate tasks like failure recovery and scaling.
