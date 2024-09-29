# Recommender System

## Project Overview
This Django-based movie recommendation system leverages the IMDB dataset to generate personalized movie suggestions. The application employs Natural Language Processing (NLP) techniques to analyze user preferences and movie metadata.

## Technologies Used
- **web development**: **Django, Python, HTML/CSS**
- **Data Processing**: **Natural Language Processing (NLP)**
- **Machine Learning Techniques**: **Scikit-Learn, TF-IDF (Term Frequency-Inverse Document Frequency), Cosine Similarity**

## Getting Started

### Prerequisites
Ensure you have Python and Django installed. Then, install the necessary packages:

```bash
pip install -r requirements.txt
```

### Running the Application
Navigate to the `recomsystem` directory and execute the following commands:

1. **Import CSV Data**:
   ```bash
   python manage.py import_csv_data
   ```
   Imports movies, ratings, and tags from CSV files into the database.

2. **Train TF-IDF Model**:
   ```bash
   python manage.py train_tfidf
   ```
   Trains the TF-IDF model on movie descriptions for content-based filtering.

3. **Generate Recommendations**:
   ```bash
   python manage.py generate_recommendations
   ```
   Outputs movie recommendations based on user preferences.

### Usage
The system uses user genre preferences along with collaborative filtering to suggest relevant movies.

## Additional Notes
- Ensure the virtual environment is active when running commands.
- Database migrations may be required when models are updated. 

    ```bash
    python manage.py migrate
    ```

## Start the Development Server: Run the development server
    
  ```bash
    python manage.py runserver
  ```

## Access the Application: Open your web browser and go to http://127.0.0.1:8000/ to see your application running.

