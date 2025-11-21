
% Open file selection dialog
[file, path] = uigetfile('*.csv', 'Select a CSV file');

% Check if the user canceled the selection
if isequal(file, 0)
    disp('User canceled the file selection. Exiting.');
    return;
end

% Construct the full path to the selected file
selectedFile = fullfile(path, file);

% Read data from the selected CSV file
data = readtable(selectedFile);

timeVarName = 'Time_s_';
voltageVarName = 'Channel1_V_';


t = data.(timeVarName);
Vin = data.(voltageVarName);

Rf = 33000;
Ri = 33000;
Wc_default = 25;

% Step 2: Calculate Laplace transform of the transfer function
s = tf('s');
H = -(Rf/Ri) * Wc_default / (s + Wc_default);
H_2 = -(Rf/Ri);

% Step 3: Simulate the system response
Vout_inverted = lsim(H, Vin, t);
Vout = Vout_inverted * H_2;

% Step 4: Plot the input and output
fig = figure;

subplot(2, 1, 1);
plot(t, Vin);
title('Input Voltage vs Time');
xlabel('Time (s)');
ylabel('Input Voltage (V)');

subplot(2, 1, 2);
hVout = plot(t, Vout);
title('Output Voltage vs Time');
xlabel('Time (s)');
ylabel('Output Voltage (V)');




sliderX = uicontrol('Style', 'slider', ...
    'Min', 0, 'Max', 10000, 'Value', Wc_default, ...
    'Units', 'normalized', 'Position', [0.05 0.01 0.9 0.05], ...
    'SliderStep', [1/10000, 10/10000], ...
    'BackgroundColor', [0.8 0.8 0.8], ...  % Light gray background
    'ForegroundColor', [0.2 0.6 1], ...    % Blue foreground color
    'Callback', @(src, ~) updateValue(src, Vin, t, Ri, Rf, s, hVout));


% Define a structure to hold the simulation data
simData.time = t;
simData.signals.values = Vout;
simData.signals.dimensions = 1; % Number of dimensions (1 for scalar signal)

% Save the structure to the workspace for use in Simulink
assignin('base', 'simData', simData);


function updateValue(slider, Vin, t, Ri, Rf, s, hVout)
    new_Wc = slider.Value;
    H = -(Rf/Ri) * new_Wc / (s + new_Wc);
    H_2 = -(Rf/Ri);
    % Step 3: Simulate the system response
    Vout_inverted = lsim(H, Vin, t);
    Vout = Vout_inverted * H_2;

    updatePlot(hVout, Vout);
    disp(new_Wc)
end


function updatePlot(plotHandle, newVout)
    set(plotHandle, 'YData', newVout);
    drawnow;
end



