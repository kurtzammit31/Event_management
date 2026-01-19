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



## Task 2 – Database Schema

### a) Schema Design

The database for the Event Management system was designed using **MongoDB**, following a **document-based NoSQL approach**. The schema was designed and visualised using **MongoDB Compass**, allowing flexible data modelling and clear representation of relationships between system entities.

The database is named **`event_management_db`** and contains the following collections:

#### venues
Stores information related to event venues:
- `name` (string)
- `address` (string)
- `capacity` (number)

#### events
Stores information related to events:
- `name` (string)
- `description` (string, optional)
- `venue_id` (string – ObjectId reference to `venues`)
- `date` (string – ISO formatted date)
- `max_attendees` (number)

#### attendees
Stores information about people attending events:
- `name` (string)
- `email` (string)
- `phone` (string, optional)

#### bookings
Represents ticket bookings made by attendees:
- `event_id` (string – ObjectId reference to `events`)
- `attendee_id` (string – ObjectId reference to `attendees`)
- `tickets` (number)
- `booking_date` (string – ISO formatted date)

#### multimedia
Represents multimedia assets related to events and venues, such as:
- event posters
- promotional videos
- venue photos  

Multimedia records are associated with either an event or a venue through reference identifiers.

This schema design maintains clear relationships between venues, events, attendees, and bookings while remaining flexible and scalable, making it suitable for an event management platform.

---

### b) Schema Deployment

The database schema was deployed using **MongoDB Atlas**, with the database hosted in the cloud. A cluster was created and configured using MongoDB Atlas tools, including secure database user authentication and IP address whitelisting.

The collections were created using **MongoDB Compass**, and each collection was populated with **mock data** in JSON format to simulate realistic system usage. This includes sample venues, events, attendees, bookings, and multimedia references.

Deployment was verified by:
- Viewing collections and documents in **MongoDB Compass**
- Successfully connecting the database to the FastAPI application
- Confirming database accessibility through test queries

This confirms that the database schema was correctly designed, deployed, and populated with mock data as required.


## Task 3C – API Documentation (Endpoints, Database Interaction & Hosting)

This section documents the RESTful API endpoints implemented using FastAPI for the Event Management system. The API provides full CRUD functionality for all main entities and includes support for multimedia file uploads and retrieval. MongoDB Atlas is used as the database, with MongoDB GridFS handling binary file storage. Validation and relationship checks are applied throughout to ensure data integrity.

---

### Base URLs

- **Local:** http://127.0.0.1:8000  
- **Hosted (Vercel):** https://event-management-ruddy-gamma.vercel.app/>

The hosted version allows the API to be accessed remotely, demonstrating real-world deployment of a database-driven web service.

---

## Health & Connectivity Endpoints

### GET /
**Purpose:**  
Confirms that the API service is running and accessible.

**Database interaction:**  
None.

---

### GET /health/db
**Purpose:**  
Verifies connectivity between the API and MongoDB Atlas.

**Database interaction:**  
Executes a MongoDB ping command (`db.command("ping")`) to confirm that the database connection is active.

---

## Venues (CRUD)

**MongoDB Collection:** `venues`

**Endpoints:**
- `POST /venues` – Create a new venue  
- `GET /venues` – Retrieve all venues  
- `GET /venues/{venue_id}` – Retrieve a venue by ID  
- `PUT /venues/{venue_id}` – Update an existing venue  
- `DELETE /venues/{venue_id}` – Delete a venue  

**Database interaction:**
- Performs create, read, update, and delete operations on the `venues` collection
- Venue IDs are validated before database access to prevent invalid ObjectId queries

---

## Events (CRUD)

**MongoDB Collection:** `events`

**Endpoints:**
- `POST /events` – Create an event linked to a venue  
- `GET /events` – Retrieve all events  
- `GET /events/{event_id}` – Retrieve an event by ID  
- `PUT /events/{event_id}` – Update an event  
- `DELETE /events/{event_id}` – Delete an event  

**Database interaction:**
- Event records are stored in the `events` collection
- `venue_id` must be a valid MongoDB ObjectId and reference an existing venue
- Venue existence is checked before inserting or updating an event

---

## Attendees (CRUD)

**MongoDB Collection:** `attendees`

**Endpoints:**
- `POST /attendees` – Create an attendee  
- `GET /attendees` – Retrieve all attendees  
- `GET /attendees/{attendee_id}` – Retrieve an attendee by ID  
- `PUT /attendees/{attendee_id}` – Update an attendee  
- `DELETE /attendees/{attendee_id}` – Delete an attendee  

**Database interaction:**
- CRUD operations are performed on the `attendees` collection
- Input data is validated using Pydantic models to enforce required fields and data types

---

## Bookings (CRUD)

**MongoDB Collection:** `bookings`

**Endpoints:**
- `POST /bookings` – Create a booking  
- `GET /bookings` – Retrieve all bookings  
- `GET /bookings/{booking_id}` – Retrieve a booking by ID  
- `PUT /bookings/{booking_id}` – Update a booking  
- `DELETE /bookings/{booking_id}` – Delete a booking  

**Database interaction:**
- Bookings link attendees to events
- Both `event_id` and `attendee_id` must be valid and reference existing documents
- Existence checks ensure valid relationships between collections

---

## File Storage & Retrieval (MongoDB GridFS)

Multimedia files such as venue photos, event posters, and promotional videos are stored using MongoDB GridFS.

- Binary file data is stored in `fs.files` and `fs.chunks`
- The generated GridFS file ID is saved in the related venue or event document
- Files are retrieved and streamed to the client using FastAPI `StreamingResponse`

A synchronous MongoDB client is used for GridFS operations, while the asynchronous Motor client is used for standard CRUD database interactions.

---

## Hosting Overview

The API is deployed using **Vercel**, allowing it to be accessed via a public URL. Hosting the API demonstrates how a FastAPI application can be connected to a cloud-hosted MongoDB Atlas database and made available remotely.

Environment variables such as the MongoDB connection string and database name are configured securely in the hosting environment to prevent credential exposure.

---

## Validation & Security Notes

- MongoDB ObjectIds are validated before all database operations
- Existence checks enforce relationships between collections
- Sensitive database credentials are stored in a `.env` file locally and as environment variables in the hosted environment


## Task 4 – Configuring Database Security

This task focuses on securing the MongoDB Atlas database used by the Event Management API. Security was implemented through (a) secure credentials, (b) IP whitelisting, and (c) input validation to reduce injection-style attacks and malformed queries.

---

### Task 4A – Secure Credentials (MongoDB Atlas Database User)

A dedicated MongoDB Atlas database user was created with a strong password to ensure that database access requires authentication.

Security measures applied:
- A unique database user account is used for the cluster.
- Credentials are not hardcoded in the application source code.
- The MongoDB connection string is stored securely in environment variables:
  - Local development uses a `.env` file.
  - The hosted deployment stores values as environment variables in the hosting provider.

Result:
- Only authenticated users with valid credentials can access the database.

Evidence (Screenshot required):
- MongoDB Atlas → **Security** → **Database Access** showing the created database user (username visible, password not shown).

---

### Task 4B – IP Address Whitelisting (Network Access)

MongoDB Atlas Network Access rules were configured to restrict connections to trusted IP addresses only.

Security measures applied:
- IP access list was configured in MongoDB Atlas to limit who can connect to the cluster.
- Only approved IP addresses are allowed (development machine / trusted network).
- This prevents unknown networks from connecting even if credentials are leaked.

Result:
- Database connections are blocked unless they originate from an approved IP address.

Evidence (Screenshot required):
- MongoDB Atlas → **Security** → **Network Access** showing IP Access List rules (allowed IPs).

---

### Task 4C – Injection Prevention / Input Validation

Although MongoDB is a NoSQL database, user input can still be abused (e.g., malformed IDs or unexpected values). The API applies strict validation to ensure that only correctly formatted inputs are accepted before database queries are executed.

Measures implemented:
- ObjectId validation is performed before any query using route parameters:
  - `ObjectId.is_valid(<id>)` is used to reject malformed IDs early.
- Request bodies are validated using Pydantic models:
  - Required fields, minimum lengths, and numeric constraints are enforced using `Field(...)`.
- Relationship integrity checks are applied:
  - Events require a valid existing `venue_id`.
  - Bookings require valid existing `event_id` and `attendee_id`.

Result:
- Invalid or malicious inputs are rejected before reaching MongoDB operations, reducing injection-style risks and preventing malformed queries.


