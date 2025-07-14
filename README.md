# OAuth Integration App

A full-stack app with **FastAPI (Python)** backend and **React** frontend that integrates OAuth login with **Notion**, **Airtable**, and **HubSpot**.

---

## Features

- OAuth 2.0 login flow
- Fetches user data after successful auth
- Unified data model across all integrations

---

## Tech Stack

- Backend: FastAPI, Python
- Frontend: React (CRA), Axios
- OAuth Providers: Notion, Airtable, HubSpot

---

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!
