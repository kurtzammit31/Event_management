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


## Task 3C – API Documentation (Endpoints & Database Interaction)

This section documents the RESTful API endpoints implemented using FastAPI for the Event Management system. Each endpoint performs CRUD operations on MongoDB collections, with validation applied to ensure data integrity. Multimedia files are stored using MongoDB GridFS, with file reference IDs saved in the relevant documents.

---

### Base URLs
- Local: http://127.0.0.1:8000  
- Hosted (Vercel): https://event-management-ruddy-gamma.vercel.app

---

## Health & Connectivity

### GET /
Purpose: Confirms the API is running.  
Database interaction: None.

### GET /health/db
Purpose: Confirms MongoDB Atlas connectivity.  
Database interaction: Executes a MongoDB ping command.

---

## Venues (Collection: `venues`)
Endpoints:
- `POST /venues` – Create a venue  
- `GET /venues` – Retrieve all venues  
- `GET /venues/{venue_id}` – Retrieve a venue by ID  
- `PUT /venues/{venue_id}` – Update a venue  
- `DELETE /venues/{venue_id}` – Delete a venue  

Database interaction:
- Writes, reads, updates, and deletes documents in the `venues` collection
- Venue IDs are validated before database operations

---

## Events (Collection: `events`)
Endpoints:
- `POST /events` – Create an event linked to a venue  
- `GET /events` – Retrieve all events  
- `GET /events/{event_id}` – Retrieve an event by ID  
- `PUT /events/{event_id}` – Update an event  
- `DELETE /events/{event_id}` – Delete an event  

Database interaction:
- Events are stored in the `events` collection
- `venue_id` must be a valid ObjectId and reference an existing venue

---

## Attendees (Collection: `attendees`)
Endpoints:
- `POST /attendees` – Create an attendee  
- `GET /attendees` – Retrieve all attendees  
- `GET /attendees/{attendee_id}` – Retrieve an attendee by ID  
- `PUT /attendees/{attendee_id}` – Update an attendee  
- `DELETE /attendees/{attendee_id}` – Delete an attendee  

Database interaction:
- CRUD operations on the `attendees` collection
- Input data validated using Pydantic models

---

## Bookings (Collection: `bookings`)
Endpoints:
- `POST /bookings` – Create a booking  
- `GET /bookings` – Retrieve all bookings  
- `GET /bookings/{booking_id}` – Retrieve a booking by ID  
- `PUT /bookings/{booking_id}` – Update a booking  
- `DELETE /bookings/{booking_id}` – Delete a booking  

Database interaction:
- Bookings link `events` and `attendees`
- Referenced event and attendee must exist

---

## File Storage & Retrieval (MongoDB GridFS)

Multimedia files (venue photos, event posters, and promotional videos) are stored using MongoDB GridFS.

- File data is stored in `fs.files` and `fs.chunks`
- The generated GridFS file ID is saved in the related venue or event document
- Files are retrieved and streamed using `StreamingResponse`

GridFS operations use a synchronous MongoDB client, while all other database operations use the asynchronous Motor client.

---

## Validation & Security Notes

- MongoDB ObjectIds are validated before database queries
- Existence checks enforce relationships between collections
- Database credentials are stored securely in a `.env` file


