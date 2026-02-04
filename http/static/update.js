
class WebSocketCustom extends WebSocketHandler
{
constructor(address="ws://localhost:5000/ws") {
	super(address);
	console.log(this.ws)
}
websocket_message(data)
{
    try {
        if(data.event == "broadcast")
        {
		switch (data.data.command) {
			case "add":
				console.log("Add: "+data.data.srt);
				add_title(data.data.srt)
				break;
			case "update":
				console.log("Upate: "+data.data.srt);
				update_title(data.data.srt)
				break;
			case "remove":
				console.log("Upate: "+data.data.srt);
				remove_title(data.data.srt)
				break;
			default:
				console.log(`Command not found ${data.data.command}.`);
		}
        }
    } catch (error) {
        alert(error);
    }
}

keepalive()
{
	console.log(this.ws)
	this.sendEvent("keepalive");
	setTimeout(this.keepalive.bind(this),10000)
}

}




const socket = new WebSocketCustom("/ws");



setTimeout(socket.keepalive.bind(socket),1000)

times=[]

class Title {
	constructor(start, end, text)
	{
		this.start = start;
		this.end = end;
		this.text = text;
	}

	update ()
	{
		fetch("/update", {
			method: 'post',
		body: {"start":this.start,"text":document.getElementById("text"+this.start).value},
		}).then(() => {
			// Do nothing
		});
	};

	element()
	{
		var form = document.createElement("form");
		form.classList.add("title-view");
		form.id="form-"+this.start;
		var h5 = document.createElement("h5");
		var span = document.createElement("span");
		span.innerText = this.start;
		h5.appendChild(span);
		var a = document.createElement("a");
		a.innerText = "X";
		a.name=this.start;
		a.classList.add("remove");
		a.onclick = function(event) {
			console.log(event.target.name);
			fetch("/remove", {
				method: 'post',
			headers: {
				"Content-Type": "application/json",
				'Accept':'application/json'
			},
			body: JSON.stringify({"start":event.target.name}),
			}).then(() => {
				// Do nothing
				//document.getElementById("form-"+event.target.name).remove();
			});
		};
		h5.appendChild(a);
		form.appendChild(h5);
		var textarea = document.createElement("textarea");
		textarea.value = this.text;
		textarea.id = "text"+this.start;
		textarea.classList.add("wide");
		form.appendChild(textarea);

		var input = document.createElement("input");
		input.type="button";
		input.classList.add("wide");
		input.value="Update";
		input.name=this.start;
		input.onclick = function(event) {
			console.log(event.target.name);
			fetch("/update", {
				method: 'post',
				headers: {
					"Content-Type": "application/json",
					'Accept':'application/json'
				},
				body: JSON.stringify({"start":event.target.name,"text":document.getElementById("text"+event.target.name).value}),
			}).then(() => {
				// Do nothing
			});
		};
		form.appendChild(input);
		var start_elm = document.createElement("input");
		start_elm.type="hidden";
		start_elm.setAttribute("name", "start");
		start_elm.value=this.start;
		form.appendChild(start_elm);
		return form
	}
}

function update_title(title)
{
	document.getElementById("text"+title["start"]).value = title["text"];
}

function remove_title(title)
{
	document.getElementById("form-"+title["start"]).remove();
}

function add_title(title)
{
	times.push(title["start"]);
	t = new Title(start=title["start"],end=title["end"],text=title["text"])
	titles=document.getElementById('titles');
	titles.insertBefore(t.element(), titles.firstChild);

	let params = new URLSearchParams(document.location.search);
	if (params.get("alarm"))
	{
		var audio = new Audio('/static/beep.wav');
		audio.play();
	}
}


function loadUpdate(event)
{
	fetch('/srt.json').then((response) => response.json())
	.then((data) =>	{
		for (const title of data) {
			if ( !times.includes(title["start"]))
			{
				add_title(title)
			}
		}
	});


	//setTimeout(loadUpdate, 10000);
}
window.addEventListener("load", loadUpdate);

function add(event) {
	fetch("/add", {
		method: 'post',
	   headers: {
		   "Content-Type": "application/json",
		   'Accept':'application/json'
	   },
	   body: JSON.stringify({"text":document.getElementById("text").value}),
	}).then(() => {
		document.getElementById("text").value = ""
	});
};

document.getElementById('new_title').onclick = add;
document.getElementById('text').addEventListener("keyup", function(event) {
	event.preventDefault();
	if (event.keyCode === 13) {
		document.getElementById("new_title").click();
	}
});
