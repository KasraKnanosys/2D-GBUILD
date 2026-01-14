# Define the Python script path
$pythonScript = "C:\Users\nsakib\Documents\Atomsk\Defect_4848\GB\gb4848.py"

# Define the output folder and file
$outputFolder = "C:\Users\nsakib\Documents\Atomsk\Defect_4848\GB"

# Create the output folder if it doesn't exist
if (-not (Test-Path -Path $outputFolder)) {
    New-Item -ItemType Directory -Path $outputFolder
}

# Initialize a hashtable to store combinations
$usedCombinations = @{}

# Loop through the range of arguments
for ($arg1 = 1; $arg1 -le 30; $arg1++) {
    for ($arg2 = 1; $arg2 -le 30; $arg2++) {
        # Skip if arg1 is equal to arg2 or combination has been used
        if ($usedCombinations["$arg1-$arg2"] -or $usedCombinations["$arg2-$arg1"]) {
            continue
        }

        # Mark this combination as used
        $usedCombinations["$arg1-$arg2"] = $true
		
		# Save the output to a file in the output folder
        $outputFilePath = Join-Path $outputFolder "\GB-$arg1-$arg2\"
		
		# Create the output folder if it doesn't exist
		if (-not (Test-Path -Path $outputFilePath)) {
			New-Item -ItemType Directory -Path $outputFilePath
		}
		
		cd $outputFilePath
		
        # Run the Python script with arguments and capture the output
        python $pythonScript $arg1 $arg2

               
        # Display a message
        Write-Host "Python script output for arguments $arg1 and $arg2 saved to $outputFilePath"
    }
}

# Display completion message
Write-Host "All combinations processed and saved."