import React, { ChangeEvent, useState } from 'react';
import './App.css';



class FileUpload extends React.Component<{}, {}> {

  constructor(props: {}) {
    super(props);
  }

  onFileUpload = (event: ChangeEvent<HTMLInputElement>) => {

    if (event.target.files && event.target.files.length > 0) {

          // Create an object of formData
          const formData = new FormData();

          // Update the formData object
          formData.append(
            "myFile",
            event.target.files[0],
            event.target.files[0].name
          );

          // Details of the uploaded file
          console.log(event.target.files[0]);

          // Request made to the backend api
          // Send formData object
          // axios.post("api/uploadfile", formData);
    }
  };

  render() {
    return (
        <div className="center">
            <div className="title">
                <h1>Super light file uploader</h1>
            </div>
            <div className="dropzone">
                <img src="http://100dayscss.com/codepen/upload.svg" className="upload-icon" />
                <input type="file" className="upload-input" onChange={this.onFileUpload}/>
            </div>
        </div>
    );
  }
}

export default FileUpload;