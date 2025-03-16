function cloneInputComponent(inputName) {
	// Get the input elements by their name
	const inputElements = document.getElementsByName(inputName);

	// Check if any input elements exist
	if (inputElements.length === 0) {
		console.error(`Elements with name ${inputName} not found.`);
		return;
	}

	// Get the last input element with the specified name
	const lastInputElement = inputElements[inputElements.length - 1];

	// Clone the input element
	const clonedElement = lastInputElement.cloneNode(true);
	clonedElement.value = "";

	// Increment the second number of the cloned element's ID
	const lastId = lastInputElement.id;
	const idParts = lastId.split("_");
	const firstNumber = parseInt(idParts[1], 10);
	const secondNumber = parseInt(idParts[2], 10);
	const newId = `component_${firstNumber}_${secondNumber + 1}`;
	clonedElement.id = newId;

	// Insert the cloned element as a sibling of the last input element
	lastInputElement.parentNode.insertBefore(
		clonedElement,
		lastInputElement.nextSibling
	);
}
