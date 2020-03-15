from model import run_model, plot
from flask import Flask, Response, request
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/graph.png')
def plot_png():
    N = request.args.get('N', default = 10E6, type = int)
    I_0 = request.args.get('I_0', default = 775 / 0.1, type = int)
    R_0 = request.args.get('R_0', default = 100, type = int)
    R0 = request.args.get('R0', default = 2.5, type = float)
    t_max = request.args.get('t_max', default = 300, type = int)
    D = request.args.get('D', default = 17.5, type = float)
    y_max = request.args.get('y_max', default = 3E6, type = int)

    t, S, I, R = run_model(R0, D, N, I_0, R_0, t_max)

    fig, ax = plt.subplots(1)
    fig.suptitle('SIR model for COVID-19')
    plot(ax, t, S, I, R, y_max)

    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
