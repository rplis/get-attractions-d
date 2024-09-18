# Project Name

Brief description of your project.

## Prerequisites

- Python 3.x
- Docker (optional)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/rplis/get-attractions-d.git
   cd get-attractions-d
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the main script:
```
python main.py
```

## Docker

Build the Docker image:
```
docker build -t get-attractions .

Run the Docker container:
```
docker run -p 8080:8080 get-attractions
```

## Environment Variables

Create a `.env` file in the project root and set the following environment variables:
```
GOOGLE_MAPS_API_KEY=<your_google_maps_api_key>
```
