COVID Dashboard
===============

This is the dashboard that integrates visualizations and data scattered accross different repositories, in particular:

* [IFCA/mitma-covid](https://github.com/IFCA/mitma-covid) that parses mobility data.
* [IFCA/covid-risk-map](https://github.com/IFCA/covid-risk-map) that integrates mobility data with incidence data.
* [IFCA/covid-dl](https://github.com/IFCA/covid-dl) to train the Deep Learning models to predict future incidence.

The safest way to run the Dashboard will all it's dependencies is to run the provided Dockerfile.
If your envirronment is already prepared you can:
* run the Dash apps without the Dashboard templating with:
    ```bash
    python dash.py
    ```
* run the full Dashboard with:
    ```bash
    python run.py
    ```

### Notes
* Plotly/Dash doesn't integrate well with Jinja2, especially with the extend html feature ([ref](https://community.plotly.com/t/using-dash-in-flask-app-extend-base-html-using-jinja2/43298)). We ended up deploying Dash apps as standalones and integrating them via `iframes` as suggested [here](https://www.reddit.com/r/flask/comments/lmoc9n/using_dash_in_flask_app_how_do_i_extend_basehtml/gnw6ur2?utm_source=share&utm_medium=web2x&context=3). This resulted in a cleaner and more modular approach.
