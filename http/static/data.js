
/*
 * Wraps common functions for accessing JSON resources
 */
class JSONHandler
{
/*
 * Sends a post request containing data payload to address in a way that
 * python/flask/quart can easily decode
 */
static post(address="/api",data=null)
{
    return fetch(address, {
          method: 'post',
          headers: {
              "Content-Type": "application/json",
              'Accept':'application/json'
          },
          body: JSON.stringify(data),
    });
}

/*
 * Fetches a json URI and decodes it before returning
 */
static read(address="/api")
{
    return fetch(address, { signal: AbortSignal.timeout(15000) })
    .then((response) => response.json())
}

}

/*
 * Builder for generating structured HTML representations of data sources.
 */
class ListBuilder
{

/*
 * Replaces text in provided template using keys from dictionary as match source
 */
static d_render(template,data,parent_element=document.createElement("div"))
{
    // Duplicate parent node to add new data
    var parent = parent_element.cloneNode(true);

    // Iterate over all dictionary entries
    for (const [key, value] of Object.entries(data)) {
        // Replace all instance of %key% with value
        template=template.replace("%"+key+"%",value)
    }

    parent.innerHTML = template.trim()

    return parent
}

/*
 * Parse a list of dictionaries to render to provided HTML template
 */
static ld_render(
    template,
    data_list,
    parent_element=document.createElement("ul"),
    child_element=document.createElement("li")
){
    var parent = parent_element.cloneNode(true);
    for (const data of data_list) {
        parent.appendChild(ListBuilder.d_render(template,data,child_element))
    }
    return parent
}
}


/*
 * Matching UUID websocket handler for Python Server
 */
class WebSocketHandler
{

/*
 * Setup connection to WebSocket server
 */
constructor(address="ws://localhost:5000/ws")
{
    this.address = address;
    this.uuid=null;
    this.ws = new WebSocket(this.address);

    this.ws.addEventListener("close",this.websocket_close.bind(this));

    this.ws.addEventListener("open", (event) => {
        this.sendEvent("open");
    });

    this.ws.addEventListener("message",this.listener_message.bind(this));
}

/*
 * Wrapper class for events to handle some management tasks
 */
listener_message(event)
{
    try {
        // Get and decode JSON data to object
        var data = JSON.parse(event.data);

        // Check for new UUID from initial connection
        if( data.event && data.event == "new_uuid")
        {
            this.uuid=data.uuid;
            console.log("uuid: "+ data.uuid);
        }else if(data.event){
            // Send through all other events
            this.websocket_message(data);
        }
    } catch (error) {
        alert("Message from server "+ event.data);
    }
}

/*
 * User override function for custom logic in child class
 */
websocket_message(data)
{

}

/*
 * Send formated event data to WebSocket server
 */
sendEvent(event_name,data=null)
{
    this.ws.send(JSON.stringify({"event":event_name,"data":data}));
}

/*
 * Log connection close
 */
websocket_close(event){
    console.log("WebSocket Closed");
}

}
