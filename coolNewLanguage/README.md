## Tool Control Flow
### Initialization
When a tool is initialized, it instantiates the WebApp instance which backs it.
### Adding a stage
A stage is defined using a function (a stage-defining function, or SDF), within which we initialize Components, define 
how to process input data, and potentially display the results. 
Each Component describes an input field of the stage.
To render the stage when running the WebApp, we use a Jinja template.
To construct this template, we construct a list of HTML elements while adding the stage.
To accomplish this, the stage-defining function is called, and each time a Component is instantiated, the corresponding
HTML elements are added to the list being constructed. 
Then, when the SDF returns, we can use the list to construct the stage's HTML template.
### Processing data within a stage
When rendered, each stage becomes an HTML form.
When the form is submitted (by the user), a POST request is issued and handled by the corresponding Stage object.
To access the POST data, the SDF is run again.
As each Component is instantiated within the SDF (for the 2nd time), each Component with data associated attaches gets
it from the post body, setting it as an instance variable on itself.
Then, when the stage's Processor is run, method overloading allows the Component objects to be treated like the actual 
associated data.