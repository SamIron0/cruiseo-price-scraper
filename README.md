# Carpool Platform

The Carpool Platform is an effective web application built to streamline carpooling services. It utilizes a web scraper, based on the Selenium WebDriver, to draw out trip costs, which are then accessed by an AWS Lambda function when triggered through an AWS API Gateway by nExtsjs frontend code. The scraper is locally hosted on a MacBook server and made available with ngrok, while the frontend is hosted on Vercel. Additionally, the platform takes advantage of well-regarded technologies and services such as AWS API Gateway, FastAPI, BeautifulSoup, JSON, among others.

This repo contains only the web scraper code. Refer to the README file in the general repo @ https://github.com/SamIron0/cruiseo for the full project links.

## Key Features 
- A Selenium WebDriver-based web scraper developed to capture trip prices from Uber. 
- A scraper script is locally hosted on a MacBook server which is made accessible using Nginx.
- A RESTful API using FastAPI to facilitate interaction with a Node.js lambda function hosted on AWS as the backend service. 
- Efficient email parsing in the scraper script using Beautiful Soup.
- Use of a local script running on a uvicorn server that includes crucial modules like FastAPI, BeautifulSoup, JSON, and others.
- Secure management of environment variables via dotenv while adjusting Chrome WebDriver settings for optimum performance.

## Run

To run the Carpool web scraper code, use the following command:

```bash
uvicorn app:app
```

After setting up ngrok, use the command:

```bash
ngrok http 8000
```

## Configuration

The Carpool projects uses environment variables for configuration. Create a `.env` file in the root directory of the project and add the required variables. Refer to the `.env.example` file for the list of variables needed.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.

## License

The Carpool Platform is licensed under the MIT License.

