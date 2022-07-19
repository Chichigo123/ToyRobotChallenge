from django.http import HttpResponse
from django.views.generic.edit import FormView
from django.shortcuts import render

from .forms import UserInputForm
from toyrobot.management.commands.run_simulator import *

# Create your views here.
class ToyRobot(FormView):
    template_name = 'toyrobot/display_user_input.html'
    form_class = UserInputForm


    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        commands = []
        commands.append([form.data.get('initial_place')])
        commands.append(form.data.get('commands').split('\r\n'))
        commands = [str.upper(x) for y in commands for x in y]

        # TO DO bug when creating new setup. Currently appending new setup
        simulator = Simulator()
        simulator.setup_simulator(commands=commands)
        result = simulator.run_simulator()
        last_setup = len(result.instance()._setup) - 1
        new_position = 'ROBOT NEW POSITION: {} {} {}'.format(result.instance()._setup[last_setup]._toy_robot._position.x,
                                                             result.instance()._setup[last_setup]._toy_robot._position.y,
                                                             result.instance()._setup[last_setup]._toy_robot._position.f)
        return render(self.request, template_name=self.template_name, context={'result': new_position})
