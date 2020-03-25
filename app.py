from flask import Flask, Response, request, render_template_string
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from model import run_model, plot, initial_values
from data import data_sweden
import io
import random
from datetime import date, timedelta
from dateutil import parser

app = Flask(__name__)

def parse_date(string):
    return parser.parse(string).date()

def params():
    N, t_min, t_max, R_0, I_0, R0, D, y_max, t0_date  = initial_values()
    t0_real, t_real, _ = data_sweden()
    t0_date = t0_real + timedelta(days=int(t_real[-1]))

    N = request.args.get('N', default = int(N), type = int)
    I_0 = request.args.get('I_0', default = I_0, type = int)
    R_0 = request.args.get('R_0', default = R_0, type = int)
    R0 = request.args.get('R0', default = R0, type = float)
    t_min = request.args.get('t_min', default = t_min, type = int)
    t_max = request.args.get('t_max', default = t_max, type = int)
    D = request.args.get('D', default = D, type = float)
    y_max = request.args.get('y_max', default = int(y_max), type = int)
    t0_date = request.args.get('t0_date', default = t0_date, type = parse_date)
    return (N, t_min, t_max, R_0, I_0, R0, D, y_max, t0_date)

@app.route('/')
def root():
    N, t_min, t_max, R_0, I_0, R0, D, y_max, t0_date = params()
    return render_template_string('''
<!doctype html>
<html lang="en">
    <head>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
        <script type="text/javascript" src="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>SIR model for COVID-19</title>
    </head>
    <body>
    <div class="container">
        <a href="/">
            <h1 class="text-center">SIR model for COVID-19</h1>
        </a>
        <br>
        <form action="/" class="text-right">
            <div class="row">
            <div class="col-md-3">
              <label>N:</label>
              <input type="text" id="N" name="N" value="{{N}}"></br>
              <small class="form-text text-muted">Population size</small>
            </div>
            <div class="col-md-3">
              <label for="I_0">I_0:</label>
              <input type="text" id="I_0" name="I_0" value="{{I_0}}"><br>
              <small class="form-text text-muted">Individuals infected at t=0</small>
            </div>
            <div class="col-md-3">
              <label for="t_min">t_min:</label>
              <input type="text" id="t_min" name="t_min" value="{{t_min}}"><br>
              <small class="form-text text-muted">Days before t0 to start</small>
            </div>
            <div class="col-md-3">
              <label for="y_max">y_max:</label>
              <input type="text" id="y_max" name="y_max" value="{{y_max}}"><br>
              <small class="form-text text-muted">y scale max in graph</small>
            </div>
            </div>

            <div class="row">
            <div class="col-md-3">
              <label for="D">D:</label>
              <input type="text" id="D" name="D" value="{{D}}"><br>
              <small class="form-text text-muted">Days to recover (inc. incubation)</small>
            </div>
            <div class="col-md-3">
              <label for="R_0">R_0:</label>
              <input type="text" id="R_0" name="R_0" value="{{R_0}}"><br>
              <small class="form-text text-muted">Individuals recovered at t=0</small>
            </div>
            <div class="col-md-3">
              <label for="t_max">t_max:</label>
              <input type="text" id="t_max" name="t_max" value="{{t_max}}"><br>
              <small class="form-text text-muted">Days after t0 top stop</small>
            </div>
            <div class="col-md-3">
            </div>
            </div>

            <div class="row">
            <div class="col-md-3">
              <label for="R0">R0:</label>
              <input type="text" id="R0" name="R0" value="{{R0}}"><br>
              <small class="form-text text-muted">Nr infected from a single person</small>
            </div>
            <div class="col-md-3">
            </div>
            <div class="col-md-3">
              <label for="t0_date">t0_date:</label>
              <input type="text" id="t0_date" name="t0_date" value="{{t0_date}}"><br>
              <small class="form-text text-muted">Date of t=0 (for matching real data)</small>
            </div>
            <div class="col-md-3">
              <button type="submit" class="btn btn-primary">Compute</button>
            </div>

            </div>
        </form>
        <div class="row">
        <div class="col-md-12 text-center">
        <img src="graph/{{img_name}}.png?N={{N}}&I_0={{I_0}}&R_0={{R_0}}&R0={{R0}}&t0_date={{t0_date}}&t_min={{t_min}}&t_max={{t_max}}&D={{D}}&f={{f}}&y_max={{y_max}}" />
        </div>
        </div>
    </div>
    </body>
</html>
    ''', N=N, I_0=I_0, R_0=R_0, R0=R0, t0_date=t0_date, t_max=t_max, t_min=t_min, D=D, y_max=y_max, img_name=random.randint(0, 1E9))

fig, ax = plt.subplots(1)

@app.route('/graph/<path:path>')
def plot_png(path):
    plt.cla() # Don't create fig and ax here since plotlib keeps them alive

    N, t_min, t_max, R_0, I_0, R0, D, y_max, t0_date = params()

    t, S, I, R = run_model(R0, D, N, I_0, R_0, t_min, t_max)
    plot(ax, t, S, I, R, t0_date, y_max)

    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
