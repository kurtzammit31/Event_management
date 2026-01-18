# Event Management API

## Task 1 – Environment Setup and Technology Selection

This project is a RESTful Event Management API developed as part of the **Database Essentials** assignment. The purpose of Task 1 is to establish a clean development environment, select appropriate technologies, and document the setup clearly.

---

## 1. Technology Selection

The following technologies were selected for this project:

* **Python 3.14** – Core programming language
* **FastAPI** – Lightweight, modern web framework for building APIs
* **Uvicorn** – ASGI server used to run the FastAPI application
* **MongoDB Atlas** – Cloud-hosted NoSQL database
* **Motor** – Asynchronous MongoDB driver for Python
* **MongoDB Compass** – GUI tool for database schema design and data population
* **python-dotenv** – Used to manage environment variables securely

These technologies were chosen because they are modern, scalable, and well-suited for asynchronous database-driven web applications.

---

## 2. Development Environment Setup

### 2.1 Virtual Environment

A Python virtual environment was created to isolate project dependencies:

```bash
python -m venv env
```

The virtual environment is activated using:

```bash
env\Scripts\activate
```

---

### 2.2 Dependency Installation

All required packages were installed inside the virtual environment:

```bash
pip install fastapi uvicorn motor python-dotenv
```

Installed dependencies are tracked in the `requirements.txt` file to ensure reproducibility.

---

## 3. Project Structure

The project is organised as follows:

```
Event_management/
│── app/
│   └── main.py
│── env/
│── .env
│── .gitignore
│── requirements.txt
│── README.md
```

This structure separates application logic from configuration and environment files, improving maintainability.

---

## 4. Environment Variables Configuration

Sensitive configuration values are stored in a `.env` file:

```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/
DB_NAME=event_management_db
```

The `.env` file is excluded from version control using `.gitignore` to prevent credential exposure.

---

## 5. Running the Application

The API server is started using Uvicorn:

```bash
uvicorn app.main:app --reload
```

Once running, the API is accessible at:

* **Base URL:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **API Documentation (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 6. Database Connectivity Verification

A health check endpoint was implemented to verify MongoDB Atlas connectivity:

```
GET /health/db
```

A successful response confirms that the API is correctly connected to the cloud database.

---

## 7. Version Control

A Git repository was used to manage source code changes. The repository structure is clean, dependencies are documented, and environment-specific files are excluded.

---

## Conclusion

Task 1 successfully establishes a fully functional development environment with clearly defined technologies, secure configuration management, and proper documentation. The setup provides a solid foundation for implementing database schemas and API functionality in subsequent tasks.



## Task 2: Database Schema

### a) Schema Design

The database for the Event Management system was designed using **MongoDB**, following a **document-based NoSQL approach**. The schema was created and visualised using **MongoDB Compass**, allowing flexible data modelling and easy inspection of collections and documents.

The database is named **`event_management_db`** and contains the following collections:

- **venues**  
  Stores information about event venues, including:
  - `name` (string)
  - `address` (string)
  - `capacity` (number)

- **events**  
  Stores event details such as:
  - `title` (string)
  - `description` (string)
  - `date` (ISODate)
  - `venue_id` (ObjectId – reference to venues)
  - `price` (number)

- **attendees**  
  Stores attendee information, including:
  - `name` (string)
  - `email` (string)
  - `phone` (string)

- **bookings**  
  Represents the relationship between attendees and events:
  - `event_id` (ObjectId – reference to events)
  - `attendee_id` (ObjectId – reference to attendees)
  - `booking_date` (ISODate)
  - `tickets` (number)

- **multimedia**  
  Stores media related to events and venues:
  - `type` (string – image/video)
  - `url` (string)
  - `event_id` or `venue_id` (ObjectId)
  - `description` (string)

This schema design allows flexible expansion while maintaining clear relationships between events, venues, attendees, and bookings, which is suitable for an event management platform.

---

### b) Schema Deployment

The schema was deployed using **MongoDB Atlas**, with the database hosted in the cloud. A cluster was created and secured using MongoDB Atlas security features, including database user authentication and IP address whitelisting.

The collections were created and populated using **MongoDB Compass**. Each collection was populated with **mock data** in JSON format to simulate realistic usage of the system, including sample venues, events, attendees, bookings, and multimedia records.

Successful deployment and population were verified by:
- Viewing collections and documents in MongoDB Compass
- Connecting the database to a **FastAPI backend** using the Motor (AsyncIO) driver
- Confirming database connectivity through a health-check API endpoint

This confirms that the database schema was correctly designed, deployed, and populated with test data as required.

