import { useState, useEffect } from 'react'
import './Files.css'

function File(type, {file_id, name, size, owner}) {
	const [shared, setShared] = useState(false);

	function changeName(e) {
		const name = e.target.value
	}

	function toggleShare(e) {
		setShared(!shared);
		
	}

	let ownerDate = ( type !== "owned" ?
		<p className="owner">{owner}</p>
		: ""
	)

	return (
		<>
		<form className="file" id={file_id}>
			<input className="file-name" placeholder={name} onChange={changeName} />
			<p className="file-meta">
				<p className="file-id">{file_id}</p>
				<p className="file-size">{size}</p>
				{ ownerData }
			</p>
			<button type="button" onClick={toggleShare}></button>
		</form>
		</>
	)
}

export default function Files() {
	const [uploadFilesfile, setUpload] = useState(null);
	const [files, setFiles] = useState(null);
	const [count, setCount] = useState(1);

	useEffect(() => {
		const interval = setInterval(
			() => setCount((c) => c + 1),
			1000
		)
		fetch("/api/get/files", {method: "GET"})
		.then((resp) => resp.json())
		.then((data) => {
			setFiles(Object.entries(data).map(([type, value]) => {
				return (
					<div className={type}>
						<p className="empty">This category is empty</p>
						{value.map((file) => File(type, file))}
					</div>
				);
			}));
		});
		return () => clearInterval(interval);
	}, [count]);

	const uploadFile = (e) => {
	    if (!file) {
	      	alert('Please select a file first.');
	      	return;
	    }
	    const formData = new FormData();
	    formData.append('files', uploadFiles);
	    try {
		    fetch('/api/file/upload', {
		    	method: 'POST',
		      	body: formData,
	        }).then((response) => {
		    	if (response.ok) {
		        	alert('File uploaded successfully!');
		    	} else {
		        	alert('Upload failed.');
			    }
			});
	    } catch (error) {
	      console.error('Error uploading file:', error);
	    }
	};

	return (
		<>
			<div className="files">
				{files}
				<input className="upload" type="file"
					onChange={(e) => setUpload(e.target.files)}/>
			</div>
		</>
	);
}