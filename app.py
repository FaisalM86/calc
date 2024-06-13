from flask import Flask, request, render_template
import numpy as np

app = Flask(__name__)

class ThermalBalanceCalculator:
    def __init__(self, surfaces, lights_personnel, equipment, miscellaneous, ventilation_flow_rate, air_density, specific_heat_capacity, supply_air_temp, room_temp):
        self.surfaces = surfaces  # List of tuples: (U-value, Area, External temp)
        self.lights_personnel = lights_personnel
        self.equipment = equipment
        self.miscellaneous = miscellaneous
        self.ventilation_flow_rate = ventilation_flow_rate
        self.air_density = air_density
        self.specific_heat_capacity = specific_heat_capacity
        self.supply_air_temp = supply_air_temp
        self.room_temp = room_temp

    def calculate_heat_gain_surfaces(self):
        q_surfaces = sum(U * A * (t_ext - self.room_temp) for U, A, t_ext in self.surfaces)
        return q_surfaces

    def calculate_heat_gain_ventilation(self):
        q_ventilation = self.ventilation_flow_rate * self.air_density * self.specific_heat_capacity * (self.supply_air_temp - self.room_temp)
        return q_ventilation

    def calculate_total_heat_gain(self):
        q_surfaces = self.calculate_heat_gain_surfaces()
        q_ventilation = self.calculate_heat_gain_ventilation()
        q_total_heat_gain = q_surfaces + self.lights_personnel + self.equipment + self.miscellaneous
        return q_total_heat_gain, q_ventilation

    def find_balance(self, tolerance=1e-3):
        q_total_heat_gain, q_ventilation = self.calculate_total_heat_gain()
        q_required_reheat = - (q_total_heat_gain + q_ventilation)

        iteration = 0
        while abs(q_required_reheat) > tolerance:
            self.room_temp += q_required_reheat / (self.air_density * self.specific_heat_capacity * self.ventilation_flow_rate)
            q_total_heat_gain, q_ventilation = self.calculate_total_heat_gain()
            q_required_reheat = - (q_total_heat_gain + q_ventilation)
            iteration += 1
            if iteration > 1000:  # Avoid infinite loop
                break

        return self.room_temp, q_total_heat_gain, q_ventilation, iteration


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        surfaces = request.form.getlist('surfaces')
        surfaces = [tuple(map(float, s.split(','))) for s in surfaces]

        lights_personnel = float(request.form['lights_personnel'])
        equipment = float(request.form['equipment'])
        miscellaneous = float(request.form['miscellaneous'])
        ventilation_flow_rate = float(request.form['ventilation_flow_rate'])
        air_density = float(request.form['air_density'])
        specific_heat_capacity = float(request.form['specific_heat_capacity'])
        supply_air_temp = float(request.form['supply_air_temp'])
        room_temp = float(request.form['room_temp'])

        calculator = ThermalBalanceCalculator(surfaces, lights_personnel, equipment, miscellaneous, ventilation_flow_rate, air_density, specific_heat_capacity, supply_air_temp, room_temp)
        final_room_temp, total_heat_gain, ventilation_heat_gain, iterations = calculator.find_balance()

        return render_template('result.html', final_room_temp=final_room_temp, total_heat_gain=total_heat_gain, ventilation_heat_gain=ventilation_heat_gain, iterations=iterations)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
