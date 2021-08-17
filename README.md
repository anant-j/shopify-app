
  

# Welcome to Shopify-Internship-Application!

  

  

Hi, this is a project I made for Shopify Internship Application : Backend Developer Intern (Remote) - Summer 2021.

  

  

This is a full stack application with the following components:

  

  

1. Front-End consisting of HTML, CSS and JavaScript files

  

2. Back-End consisting of a Flask (Python) API that the front-end interacts with.

  
---

  

  

### Index

  

  

- [What does this application do?](#what-does-this-application-do)

  

  

- [What tech stack does it use?](#what-tech-stack-does-it-use)

  

  

- [How does it work?](#how-does-it-work)

  

  

- [Front End](#front-end)

  

  

- [Back End](#back-end)

  

  

- [Is this code production ready?](#is-this-code-production-ready)

  
  

- [What's next](#whats-next)

  
  

- [How is it deployed?](#how-is-it-deployed)

  

  

- [Why does the code fail when the repo is cloned?](#why-does-the-code-fail-when-the-repo-is-cloned)

  

  

- [How do I run it locally?](#how-do-i-run-it-locally)

  

  

- [Challenges I faced while developing this project](#challenges-i-faced-while-developing-this-project)

  

  

- [How much did it cost to make this service and consume the external APIs?](#how-much-did-it-cost-to-make-this-service-and-consume-the-external-apis)

  

  

- [Contributions?](#contributions)

  

  

- [Contact](#contact)

  

---

  

  

### What does this application do?

  

  

This application functions as an image repository.

  

You can upload images, delete images that you have uploaded, and can view all images uploaded by all users.

  

The back-end classifies the uploaded image as (Safe For Work or Not Safe For Work). Not Safe For Work images can only be viewed when logged in.

  

  

---

  

  

### What tech stack does it use?

  

  

The back-end service is based on Python and the framework used is Flask.

  

  

Here are the external APIs used:

  

  

|API | Purpose|
| -- | -- |
|Google's Firebase Cloud Storage| Storing images in the cloud.
|Google's Firebase Cloud Firestore| To store user's statistics.
|Clarifai API| To determine if an image is SFW or NSFW.
|Discord Oauth 2.0| Log in implemented via Discord.

![Tech Stack](https://storage.googleapis.com/imgr-repo.appspot.com/VitdDVmdBf4tDwJoAuP5Qp5sTTIa4rno.png)  

---

### How does it work?

##### Front-End:

1. When someone visits the website, the user data is fetched. If the user is not logged in, they can only view the public images.

2. When the user is logged in, they can upload images, view NSFW images, and view their own gallery where they can delete the images.

3. API Operations are:

- Login

- Getting user data

- Getting all SFW images

- Uploading an image

- Getting all NSFW images

- Getting all user's images

- Deleting an image

- Logout

  

##### Back-End:

The flask back-end has the following endpoints with their functionalities:

| Endpoint | Description | Login Required
|--|--| --
| login | Returns a Discord Oauth link that the user is redirected to | ❌
| callback | Called by the Discord's Oauth servers to verify login and return to the main webpage| :heavy_check_mark:
|userdata| Returns the user's email, as well as their upload statistics| :heavy_check_mark:
|userimages| Returns links to all the images uploaded by the user| :heavy_check_mark:
|get_all_sfw| Returns links to all SFW images | ❌
|get_all_nsfw| Returns links to all SFW images |:heavy_check_mark:
|upload| 1. Uploads image temporarily to storage and get public url<br>2. Runs this public URL though Clarifai NSFW model, check if image is SFW or NSFW<br>3.Uploads the image with the correct metadata<br>4. Updates user's statistics|:heavy_check_mark:
|delete| Deletes the user specified image by obtaining image and checking if the uploader is the same as requester | :heavy_check_mark:
|logout| Logs out current user | :heavy_check_mark:


Database Structure:
![Database Structure](https://i.imgur.com/8uHwCrt.png)

Storage Structure:
![enter image description here](https://i.imgur.com/CXKZ7IU.png)
---

  

### Is this code production ready?

The code (back end and front end) can be deployed for testing once the secret keys have been included. Kindly look at [this](https://github.com/anant-j/shopify-app/tree/main/Back-End) for more info.

  

While edge cases have been considered, errors might still arise in the code.

This code is **not** suitable to be used in production applications.

  

---

  

### What's Next?

Some potential future features:

- Rate limiting based on number of uploads/requests in a minute.

- Free/Paid subscriptions with different size caps.

- Using Clarifai API to autogenerate relevant tags for uploaded images and then implementing image search with said tags.

  

---

 
#### Front-End

  

Front end is stored on my personal GitHub repository and deployed via **Netlify**.

#### Back-End

Back end is stored and deployed on **DigitalOcean**

  

>The deployed version of this application has been limited to 5 uploads per user. If using the test account mentioned on the website, the uploaded images will be deleted after 30 minutes automatically.

---

  

### Why does the code fail when the repo is cloned?

  

Since the code is dependent on multiple APIs, it needs the secret keys inside the [Back-End](./Back-End) folder to run. Methods to obtain the secret keys can be found [here](./Back-End).

  

#### How do I run it locally?

  

To run the service locally:

- Clone the repository onto local system.

- Obtain the various API keys and store in the Back-End folder. (The project is dependent on all those different APIs. Please reach out to me at [my email](#contact) if any help is required.

  

In the [Back-End](./Back-End) folder:

  

- Run [main.py](Back-End/main.py)

  

- Go to http://127.0.0.1:5000/login to view the Discord login link.

  

- Check for errors if any.

  

- Expose the API to the internet using a service like **[ngrok](https://ngrok.com/)** or **[digitalocean](http://digitalocean.com/)**.

Please consider that [Flask’s built-in server is not suitable for production](https://flask.palletsprojects.com/en/1.1.x/deploying/)

  

---

### Challenges I faced while developing this project:

I faced a few challenges when developing this service.

  

I consider these to be basic lessons for anyone developing consumer-facing APIs:

  

- Bypassing **CORS** (Cross Origin Resource Sharing) to allow browsers to consume APIs.

  

- Isolation and User Access

User's credentials are obtained on the server-side and not the client side.

Verification is performed when deleting or viewing personal gallery.

  

- Securing endpoints with either

a) OAuth JWT Tokens

  

b) API Keys

  

c) Cookie forwarding with headers

  

d) SSL or certificate verification

e) Third Party Oauth Services (Eg: **Discord**, Google Firebase Auth, etc)

  

- Deployment : **Continuous integration** with whatever deployment you are using. Changing the same code at 2 different places (GitHub and host) is a very tedious process, which might create redundancy and disparity between working code.

  

- Deployment : Setting up an API **Alert** if the server/deployment goes down. I used **[Uptime Robot](www.uptimerobot.com)** for this.

  

  

---

### How much did it cost to make this service and consume the external APIs?:

  

  

It cost me **_$0_** to make this API service.

  

  

Yes I did consumer external APIs, however, all of them are either free or offer a free tier/trial account.

  

- The Hosting at DigitalOcean was free of cost (for the first 60 days).

- Google Firebase offers a free and fair usage quota.

- Clarifai API offers a free monthly usage quota.

- Netlify offers free hosting for front-end

  

**What about Usage Limits?**

  

  

Yes, there are some motnhly/daily usage limits. However, these limits are way higher than the usual consumption for our use cases. In our deployment, each user is limited to 5 images

  

  

---

  

  

### What is the SDLC for API Development?

  

  

API Development from scratch usually involves the same 5 steps as any code release does:

  

  

#### - Design

  

  

- Before development begins, there needs to be a design document that states the different endpoints the API would have, and how each of these endpoints work.

  

  

- This is known as **Design First** Based Approach

  

  

- For each piece of code written in your life, you would have an idea of what you were doing before you began coding, just writing these ideas into a document solidifies your design principles and ensures consistency.

  

  

- Tools: SwaggerHub

  

  

#### - Create

  

  

- Once the API is designed, it is built with respect to the design document, with required changes to both the code as well as the document being made on the fly.

  

  

- Tools: Python with Flask, Java + SpringBoot + Maven, Python with Django, Ruby on Rails, NodeJS

  

  

#### - Test

  

  

- Once the API is ready to be published, it should be tested thoroughly. This should be done by adopting different testing methodologies, such as Unit Testing, Integration Testing, White and Black box testing.

  

  

- This is where load testing should be done for your API as well.

  

  

- Tools: LoaderIo, CrossBrowserTesting, CORS test

  

  

#### - Deploy

  

- Once your API is tested and ready to be released into production, it can be run locally and exposed to the internet via a self hosted server or external services such as Ngrok.

  

- The industry standard is to release APIs to the cloud using services such as AWS, Google Cloud Platform, DigitalOcean or small scale platforms like PythonAnywhere.

  

  

#### - Monitor

  

  

- Monitoring tools should be set up to measure performance of the deployed API.

  

  

- This can either be done manually by setting up loggers and reviewing them frequently.

  

  

- Another method is to set up automatic performance measurement tools which measure important KPIs for your API.

  

  

- Tools: AlertSite, UptimeRobot

  

  

---

  

### Contributions?

  

Since this project was developed as a personal project, I would not accept any contributions.

  

#### Contact

  

  

- If you want to discuss something else, kindly email me at anant.j2409@gmail.com

  

---

  

  

> Author: Anant Jain

  

**_END_**

  

  

---
