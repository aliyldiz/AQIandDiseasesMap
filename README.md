# Django AQI Diseases Map

[https://github.com/aliyldiz/Django-AQI-Diseases-Map/assets/136450832/793d74ce-c29d-45b5-8f64-7779cfa88ff0](https://github.com/aliyldiz/Django-AQI-Diseases-Map/assets/136450832/793d74ce-c29d-45b5-8f64-7779cfa88ff0
)

# Screenshots

<img width="1797" alt="1" src="https://github.com/aliyldiz/Django-AQI-Diseases-Map/assets/136450832/812d7f92-cde9-4024-bc99-a288f5f8713c">   
<img width="1798" alt="2" src="https://github.com/aliyldiz/Django-AQI-Diseases-Map/assets/136450832/da31df1a-36c8-444a-a229-786eeb36f7ed">   
<img width="1262" alt="3" src="https://github.com/aliyldiz/Django-AQI-Diseases-Map/assets/136450832/e023f54f-0adc-4173-bc5a-622ffcbb9126">   
<img width="1798" alt="4" src="https://github.com/aliyldiz/Django-AQI-Diseases-Map/assets/136450832/e13756f5-e4a1-419b-9cb1-232c86e7e7ad">   
<img width="1796" alt="5" src="https://github.com/aliyldiz/Django-AQI-Diseases-Map/assets/136450832/a342bec6-954e-4bf4-9ed6-371f78f6c2ba">

## Overview

Django AQI Diseases Map is a web application that provides an interactive map using Air Quality Index (AQI) and respiratory disease data. This project allows users to visualize air pollution levels in specific regions and their correlation with respiratory diseases.

## Features

- Display Air Quality Index (AQI) data.
- Visualize respiratory disease data.
- Interactive map for data visualization.
- Compare data between different regions.
- User-friendly interface.

## Data Sources

The datasets used in this project are sourced from:

[World Health Organization (WHO) - Respiratory Diseases](https://platform.who.int/mortality/themes/theme-details/topics/topic-details/MDB/respiratory-diseases)  
[World Health Organization (WHO) - Air Quality Database](https://www.who.int/data/gho/data/themes/air-pollution/who-air-quality-database)

### Installation

1. **Clone the repository:**

    ```
    git clone https://github.com/aliyldiz/Django-AQI-Diseases-Map.git
    cd Django-AQI-Diseases-Map
    ```

2. **Create and activate a virtual environment:**

    ```
    python -m venv env
    source env/bin/activate  # On Windows: .\env\Scripts\activate
    ```

3. **Install the required packages:**

     ```
     pip install -r requirements.txt
     ```

4. **Create the database and run the migrations:**

    ```
    python manage.py migrate
    ```

5. **Start the server:**

    ```
    python manage.py runserver
    ```

6. **Open your browser and visit:**

    ```
    [python manage.py migrate](http://127.0.0.1:8000/
    ```

## Usage

- On the home page, select a specific region to view the air quality and respiratory disease data for that area.  
- Click on markers on the map to get detailed information.
- Compare different regions to analyze air quality and disease data across multiple locations.

## Contributing

We welcome contributions! To contribute, please follow these steps:

### Steps to Contribute

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/FeatureName`.
3. Make your changes: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature/FeatureName`.
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries or issues, please contact [Ali Yildiz](https://github.com/aliyldiz).
