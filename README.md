# Final Project

## Overview

<p>This project is a FastAPI-based web application that manages a music library. It allows users to upload, download, view, update, delete music tracks, and create playlists. The project interacts with a PostgreSQL database to store metadata about the music tracks and saves the actual music files locally on the server.</p>

## Features

<ul>
  <li><b>Upload Music:</b> Upload <code>.mp3</code> files with metadata (name, author, size).</li>
  <li><b>Download Music:</b> Download music files by their ID.</li>
  <li><b>View Music Information:</b> Get details about all music tracks or a specific track by ID.</li>
  <li><b>Update Music:</b> Update the metadata and file of an existing track.</li>
  <li><b>Delete Music:</b> Delete a specific music track or all tracks.</li>
  <li><b>Create Playlist:</b> Generate a playlist with a specified number of random tracks.</li>
</ul>

## Project Structure

<pre>
project-root
│
├── main.py                   # Main application file
├── models.py                 # SQLAlchemy models for the database
├── music_files/              # Directory to store music files
│
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
└── ...
</pre>

## Requirements

<ul>
  <li>Python 3.8+</li>
  <li>PostgreSQL</li>
  <li>FastAPI</li>
  <li>SQLAlchemy</li>
  <li>Pydantic</li>
  <li>Starlette</li>
  <li>Uvicorn</li>
</ul>

## Installation

<ol>
  <li><b>Clone the repository:</b>
    <pre>
    git clone &lt;repository_url&gt;
    cd &lt;repository_directory&gt;
    </pre>
  </li>
  <li><b>Install the required Python packages:</b>
    <pre>
    pip install -r requirements.txt
    </pre>
  </li>
  <li><b>Setup PostgreSQL Database:</b>
    <ul>
      <li>Ensure PostgreSQL is installed and running.</li>
      <li>Create a database named <code>postgres</code>.</li>
      <li>Update the database connection settings in the <code>main.py</code> file if necessary.</li>
    </ul>
  </li>
  <li><b>Create necessary directories:</b>
    <pre>
    mkdir music_files
    </pre>
  </li>
</ol>

## Running the Application

<p>To start the FastAPI application, run:</p>

<pre>
uvicorn main:app --reload
</pre>

<p>This will start the server at <a href="http://127.0.0.1:3333">http://127.0.0.1:3333</a>.</p>

## API Endpoints

### Upload Music

<ul>
  <li><b>URL:</b> <code>/upload/</code></li>
  <li><b>Method:</b> <code>POST</code></li>
  <li><b>Request Parameters:</b>
    <ul>
      <li><code>file</code> (UploadFile): The <code>.mp3</code> file to upload.</li>
      <li><code>name</code> (str): The name of the music track.</li>
      <li><code>author</code> (str): The author of the music track.</li>
      <li><code>size</code> (float): The size of the music track in MB.</li>
    </ul>
  </li>
  <li><b>Response:</b> The metadata of the uploaded music track.</li>
</ul>

### Download Music

<ul>
  <li><b>URL:</b> <code>/download/{music_id}</code></li>
  <li><b>Method:</b> <code>GET</code></li>
  <li><b>Response:</b> The requested music file.</li>
</ul>

### Get All Music Information

<ul>
  <li><b>URL:</b> <code>/music_names/</code></li>
  <li><b>Method:</b> <code>GET</code></li>
  <li><b>Response:</b> List of all music tracks' metadata.</li>
</ul>

### Get Music Information

<ul>
  <li><b>URL:</b> <code>/music/{music_id}</code></li>
  <li><b>Method:</b> <code>GET</code></li>
  <li><b>Response:</b> The metadata of the specified music track.</li>
</ul>

### Create Playlist

<ul>
  <li><b>URL:</b> <code>/playlist/{track_count}</code></li>
  <li><b>Method:</b> <code>GET</code></li>
  <li><b>Response:</b> List of metadata for the generated playlist.</li>
</ul>

### Update Music

<ul>
  <li><b>URL:</b> <code>/music/{music_id}</code></li>
  <li><b>Method:</b> <code>PUT</code></li>
  <li><b>Request Parameters:</b>
    <ul>
      <li><code>name</code> (str): The new name of the music track.</li>
      <li><code>author</code> (str): The new author of the music track.</li>
      <li><code>size</code> (float): The new size of the music track in MB.</li>
      <li><code>file</code> (UploadFile, optional): The new <code>.mp3</code> file.</li>
    </ul>
  </li>
  <li><b>Response:</b> Success message.</li>
</ul>

### Delete Music

<ul>
  <li><b>URL:</b> <code>/music/{music_id}</code></li>
  <li><b>Method:</b> <code>DELETE</code></li>
  <li><b>Response:</b> Success message.</li>
</ul>

### Delete All Music

<ul>
  <li><b>URL:</b> <code>/music/</code></li>
  <li><b>Method:</b> <code>DELETE</code></li>
  <li><b>Response:</b> Success message.</li>
</ul>

## Author

### by [Anton Anpilohov](https://github.com/tosentai)
