from flask import Flask, Response, request, render_template_string
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from model import run_model, plot
import io
import random

app = Flask(__name__)

def params():
    N = request.args.get('N', default = int(10E6), type = int)
    I_0 = request.args.get('I_0', default = int(775 / 0.1), type = int)
    R_0 = request.args.get('R_0', default = 100, type = int)
    R0 = request.args.get('R0', default = 2.5, type = float)
    t_max = request.args.get('t_max', default = 300, type = int)
    D = request.args.get('D', default = 17.5, type = float)
    y_max = request.args.get('y_max', default = int(3E6), type = int)
    return (N, I_0, R_0, R0, t_max, D, y_max)

@app.route('/')
def root():
    N, I_0, R_0, R0, t_max, D, y_max = params()
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
        <h1 class="text-center">SIR model for COVID-19</h1>
        <br>
        <form action="/" class="text-right">
            <div class="row">
            <div class="col-md-3 col-md-offset-1">
              <label>N:</label>
              <input type="text" id="N" name="N" value="{{N}}"></br>
              <small class="form-text text-muted">Population size</small>
            </div>
            <div class="col-md-3">
              <label for="I_0">I_0:</label>
              <input type="text" id="I_0" name="I_0" value="{{I_0}}"><br>
              <small class="form-text text-muted">Individuals initially infected</small>
            </div>
            <div class="col-md-3">
              <label for="t_max">t_max:</label>
              <input type="text" id="t_max" name="t_max" value="{{t_max}}"><br>
              <small class="form-text text-muted">Max days to run model</small>
            </div>
            </div>

            <div class="row">
            <div class="col-md-3 col-md-offset-1">
              <label for="D">D:</label>
              <input type="text" id="D" name="D" value="{{D}}"><br>
              <small class="form-text text-muted">Days to recover</small>
            </div>
            <div class="col-md-3">
              <label for="R_0">R_0:</label>
              <input type="text" id="R_0" name="R_0" value="{{R_0}}"><br>
              <small class="form-text text-muted">Individuals initially recovered</small>
            </div>
            <div class="col-md-3">
              <label for="y_max">y_max:</label>
              <input type="text" id="y_max" name="y_max" value="{{y_max}}"><br>
              <small class="form-text text-muted">y scale max in graph</small>
            </div>
            </div>

            <div class="row">
            <div class="col-md-3 col-md-offset-1">
              <label for="R0">R0:</label>
              <input type="text" id="R0" name="R0" value="{{R0}}"><br>
              <small class="form-text text-muted">Nr infected from a single person</small>
            </div>
            <div class="col-md-3">
            </div>
            <div class="col-md-3">
              <button type="submit" class="btn btn-primary">Compute</button>
            </div>
            </div>
        </form>
        <div class="row">
        <div class="col-md-12 text-center">
        <img src="graph/{{img_name}}.png?N={{N}}&I_0={{I_0}}&R_0={{R_0}}&R0={{R0}}&t_max={{t_max}}&D={{D}}&y_max={{y_max}}" />
        </div>
        </div>
    </div>
    </body>
</html>
    ''', N=N, I_0=I_0, R_0=R_0, R0=R0, t_max=t_max, D=D, y_max=y_max, img_name=random.randint(0, 1E9))

fig, ax = plt.subplots(1)

@app.route('/graph/<path:path>')
def plot_png(path):
    plt.cla() # Don't create fig and ax here since plotlib keeps them alive

    N, I_0, R_0, R0, t_max, D, y_max = params()

    t, S, I, R = run_model(R0, D, N, I_0, R_0, t_max)

    plot(ax, t, S, I, R, y_max)

    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
