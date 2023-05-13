[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/U95dUAR4)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-718a45dd9cf7e7f842a935f5ebbe5719a5e09af4491e668f4dbf3b35d5cca122.svg)](https://classroom.github.com/online_ide?assignment_repo_id=10873508&assignment_repo_type=AssignmentRepo)

# Internship Recruitment Task
## Submission by: Sai Shashaank R

&nbsp;

## Overview

1. [Abstract](#1abstract)
1. [Salient features](#2salient-features)
1. [OAuth](#3oauth)
1. [Pre-requisites](#4pre-requisites)
1. [How to use](#5how-to-use)
1. [Database](#6database)
1. [Further Modifications](#7further-modifications)

&nbsp;

## 1.*Abstract:*

The python based application uses github OAuth to download user and their associated organization data (repo data) and stores it in a **Postgres database**. 

The application is also containerized using **docker-compose** which allows the user to run the program by just using docker-compose without the hassle of setting up postgres database.

&nbsp;

## 2.*Salient Features*

* > **docker-compose:** The application uses docker-compose to create a postgres image which is then used to store data

* **Error-handling:** All the frequently occuring errors during authentication and database insertions are logged for user convenience.

* **Data normalization:** Database consists of two tables in order to normalize data and prevent duplication. (Explained in detail in Section 6)
  
* **Network handling:** The application automatically checks and waits for network connection to be restored if not present.

&nbsp;

## 3.*OAuth*

Performing basic OAuthentication using the requests library.

Since this is a python based CLI, ***device flow*** will be used

Overview of the device flow (steps)

  1)Your app requests device and user verification codes and gets the authorization URL where the user will enter the user verification code.

  2)The app prompts the user to enter a user verification code at https://github.com/login/device.

  3)The app polls for the user authentication status. Once the user has authorized the device, the app will be able to make API calls with a new access token.

## 4.*Pre-requisites*

###    **4.1. Python3**


Ensure that python3 is installed.

Use the following command in terminal to check python3 version:

```bash
python3 --version
```

If python3 is not present, install as follows:

```bash
sudo apt update
sudo apt install python3
```

###    **4.2. psycopg**
psycopg is a python package used to connect to psql database.

Install psycopg as follows:

```bash
pip3 install psycopg
pip3 install "psycopg[binary]"
```

###    **4.3. docker, docker-compose**

Refer to the following documentation to install docker and docker-compose.

[Docker installation](https://docs.docker.com/engine/install/)

[Docker Compose](https://docs.docker.com/compose/install/linux/)


Check the docker and docker-compose versions using the commands:

```bash
docker version
docker-compose version
```

> Note: In case you get the error: Got permission denied while trying to connect to the Docker daemon socket... , refer [this link](https://www.digitalocean.com/community/questions/how-to-fix-docker-got-permission-denied-while-trying-to-connect-to-the-docker-daemon-socket)

&nbsp;

## 5.*How to use*

> Download the code files to your system.

&nbsp;

5.1. Open the project directory in a terminal and follow the instructions given below.

&nbsp;

5.2. If you already have psql installed then please execute the following command in your terminal to kill all active psql processes.

```bash
sudo pkill -u postgres
```

> This is to ensure that none of the processes interfere with the postgres image created using docker-compose.

&nbsp;

5.3. Run the following command to aggregate and run the required containers as specified in the *docker-compose.yaml* file.

```bash
docker-compose up -d
```

> This will start the psql server in the background.

&nbsp;

5.4. Run the **main.py** script as follows:

```bash
python3 main.py
```

&nbsp;

5.5. Follow the onscreen instructions. You will be required to open a link and enter the verification code after logging in.

&nbsp;

5.6. The user repo data along with the repo data of any ***organization*** that the user is part of will be stored in the database and displayed on screen.

&nbsp;

5.7. The required data will be finally stored in the csv file called **resultsFile.csv** in the **project directory**.

&nbsp;
>NOTE:

> If the user accidentally presses y without authenticating, the program detects it and shows an error.

> The program automatically detects whether or not a network connection is present. If not, it waits for a connection. The user can quit the program by pressing ***ctrl+c***

&nbsp;

## 6.*Database*

> The database has two tables owner_info and repo_info, to store the owner(user or organization) information and repository information respectively.

This is done to ensure that the owner information is stored only once in the corresponding table and all their repository information is stored in repo_info table.

> The script performs a *de-duplication check* to ensure that the owner information is not stored more than once.

&nbsp;

***Schema***

![Screenshot from 2023-04-20 22-36-39](https://user-images.githubusercontent.com/96949956/233438285-eba07b6b-b596-4f93-b966-072aa08a0d83.png)

The **foreign key "ownerId"** is used to link the  ***repo_info*** table to the  ***owner_info***  table. It receives its values from the **primary key ownerId of  *owner_info***  table.

## 7.Further Modifications

It is possible to containerize the entire application by using an **ubuntu image** as a base and then installing all the additional packages using **RUN** and **CMD** in a ***Dockerfile***. 

The container thus produced can be **pushed to docker hub**.

> This will however increase the size of the application (taking into account the size of various images) and may also affect the application execution time. Hence, was not implemented here.

