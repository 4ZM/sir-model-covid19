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
<html>
    <head>
        <title>SIR model for COVID-19</title>
    </head>
    <body>
        <h1>SIR model for COVID-19</h1>
        <form action="/">
            <label for="N">N:</label><br>
            <input type="text" id="N" name="N" value="{{N}}"><br><br>
            <label for="I_0">I_0:</label><br>
            <input type="text" id="I_0" name="I_0" value="{{I_0}}"><br><br>
            <label for="R_0">R_0:</label><br>
            <input type="text" id="R_0" name="R_0" value="{{R_0}}"><br><br>
            <label for="R0">R0:</label><br>
            <input type="text" id="R0" name="R0" value="{{R0}}"><br><br>
            <label for="t_max">t_max:</label><br>
            <input type="text" id="t_max" name="t_max" value="{{t_max}}"><br><br>
            <label for="D">D:</label><br>
            <input type="text" id="D" name="D" value="{{D}}"><br><br>
            <label for="y_max">y_max:</label><br>
            <input type="text" id="y_max" name="y_max" value="{{y_max}}"><br><br>
            <input type="submit" value="Submit">
        </form>
        <img src="graph/{{img_name}}.png?N={{N}}&I_0={{I_0}}&R_0={{R_0}}&R0={{R0}}&t_max={{t_max}}&D={{D}}&y_max={{y_max}}" />
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
