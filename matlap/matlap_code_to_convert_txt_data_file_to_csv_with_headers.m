% Open file selection dialog
[file, path] = uigetfile('*.txt', 'Select a text file');

% Check if the user canceled the selection
if isequal(file, 0)
    disp('User canceled the file selection. Exiting.');
    return;
end

% Construct the full path to the selected file
selectedFile = fullfile(path, file);

% Read data from the selected text file
data = dlmread(selectedFile);

% Extract columns
column1 = data(:, 1);
column2 = data(:, 2);

% Extract file name and extension
[~, fileName, fileExt] = fileparts(file);

% Construct output CSV file name
csvFileName = [fileName '_output.csv'];

% Write data to CSV file with headers
header = {'Time (s)', 'Channel 1 (V)'};
dataWithHeader = [header; num2cell([column1, column2])];

% Write data to CSV file
writecell(dataWithHeader, csvFileName);

disp(['Data has been successfully written to ' csvFileName]);
