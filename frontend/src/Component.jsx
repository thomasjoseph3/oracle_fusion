/* eslint-disable react/prop-types */
import { useState, useRef } from "react";
import html2canvas from "html2canvas";
import "./App.css";
import Chart from "./components/Chart";
import Table from "./components/Table";
import Card from "./components/Card";
import { PDFDocument } from "pdf-lib";
import { saveAs } from "file-saver";
import useQueryExecutor from "./hooks/useQueryExecutor";

const Component = ({ message }) => {
  const divRef = useRef();
  const [selected, setSelected] = useState(null);
  const [selectedSuggestion] = useState(null);
  const { executeQuery } = useQueryExecutor(); // Use the custom hook

  const handleDislikeClick = () => {
    setSelected("dislike");
  };

  const handleSuggestionClick = (suggestion) => {
    executeQuery(suggestion, false); //  Execute query on suggestion click
    window.scrollTo({ top: 0, behavior: "smooth" });

  };

  const downloadAsPDF = async () => {
    const div = divRef.current;
    if (!div) return;

    // Expand width to capture all scrollable content
    const originalWidth = div.style.width;
    div.style.width = div.scrollWidth + "px";

    // Capture full content
    const canvas = await html2canvas(div, {
      scale: 2,
      scrollX: -window.scrollX,
      scrollY: -window.scrollY,
      windowWidth: div.scrollWidth,
      windowHeight: div.scrollHeight,
    });

    // Reset width after capturing
    div.style.width = originalWidth;

    // Convert canvas to image
    const imgData = canvas.toDataURL("image/png");

    // Create PDF
    const pdfDoc = await PDFDocument.create();
    const page = pdfDoc.addPage([canvas.width, canvas.height]);
    const jpgImage = await pdfDoc.embedPng(imgData);

    // Draw image on PDF
    page.drawImage(jpgImage, {
      x: 0,
      y: 0,
      width: canvas.width,
      height: canvas.height,
    });

    // Save PDF
    const pdfBytes = await pdfDoc.save();
    const blob = new Blob([pdfBytes], { type: "application/pdf" });
    saveAs(blob, "download.pdf");
  };

  return (
    <div className="mt-6 w-full max-w-3xl bg-white p-6 rounded-lg shadow-lg">
      {message.user ? (
        <div>
          <h2 className="text-base font-medium mb-4">{message.text}</h2>
        </div>
      ) : message.error ? (
        <div>
          <h2 className="text-base font-medium mb-4">{message.text}</h2>
        </div>
      ) : message.no_data ? (
        <div>
          <h2 className="text-base font-medium mb-4">{message.text}</h2>
        </div>
      ) : (
        <div className="mt-6 w-full max-w-3xl bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-base font-medium mb-4">{message.question}</h2>
          <p className="text-gray-600 mb-2">{message?.description}</p>
          <hr className="mt-6 mb-6 -mx-6" />

          <div ref={divRef} style={{ overflowX: "scroll" }}>
            {message.graph && <Chart data={message.graph} />}
            {message.table && <Table data={message.table} />}
            {message.text && <Card data={message.text} />}
          </div>
          <div className="grid grid-cols-2 gap-2 h-auto rounded-lg p-2 m-2 overflow-hidden">
            {message.suggestions.slice(0, 3).map((suggestion, index) => (
              <div
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className={`p-2 bg-gray-100 rounded-full flex items-center justify-center text-center overflow-hidden text-sm cursor-pointer transition duration-200 ${
                  selectedSuggestion === suggestion
                    ? "bg-blue-300"
                    : "hover:bg-blue-200"
                } ${index === 2 ? "col-span-2" : ""}`} // M
              >
                <span className="block w-full">{suggestion}</span>
              </div>
            ))}
          </div>

          <hr className="mt-6 mb-6 -mx-6" />
          <div className="flex justify-between  mt-6">
            <div className="flex items-center px-4 py-2 text-blue-500 rounded-lg space-x-1 border border-[#DFE8EC] w-32">
              <svg
                width="20"
                height="20"
                viewBox="0 0 20 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M9.99681 12.6876C9.89681 12.6876 9.80306 12.6703 9.71556 12.6355C9.62806 12.6008 9.54959 12.5487 9.48014 12.4793L6.52181 9.52095C6.36903 9.36943 6.29612 9.19269 6.30306 8.99075C6.31 8.78866 6.38653 8.61123 6.53264 8.45846C6.69209 8.30568 6.8725 8.22929 7.07389 8.22929C7.27528 8.22929 7.45237 8.30568 7.60514 8.45846L9.25098 10.1251V3.75012C9.25098 3.53762 9.32244 3.3595 9.46535 3.21575C9.60827 3.072 9.78535 3.00012 9.9966 3.00012C10.2079 3.00012 10.3864 3.072 10.5322 3.21575C10.6781 3.3595 10.751 3.53762 10.751 3.75012V10.1251L12.4176 8.45846C12.5658 8.30568 12.7417 8.23276 12.9454 8.23971C13.1491 8.24665 13.3307 8.32651 13.4901 8.47929C13.6363 8.63207 13.7093 8.80915 13.7093 9.01054C13.7093 9.21193 13.6329 9.38901 13.4801 9.54179L10.5218 12.4793C10.4468 12.5487 10.3656 12.6008 10.2781 12.6355C10.1906 12.6703 10.0968 12.6876 9.99681 12.6876ZM5.49514 16.0001C5.08237 16.0001 4.73014 15.8532 4.43848 15.5595C4.14681 15.2657 4.00098 14.9126 4.00098 14.5001V13.7501C4.00098 13.5376 4.07243 13.3595 4.21535 13.2157C4.35827 13.072 4.53535 13.0001 4.7466 13.0001C4.95785 13.0001 5.13639 13.072 5.28223 13.2157C5.42806 13.3595 5.50098 13.5376 5.50098 13.7501V14.5001H14.501V13.7501C14.501 13.5376 14.5724 13.3595 14.7154 13.2157C14.8583 13.072 15.0354 13.0001 15.2466 13.0001C15.4579 13.0001 15.6364 13.072 15.7822 13.2157C15.9281 13.3595 16.001 13.5376 16.001 13.7501V14.5001C16.001 14.9126 15.854 15.2657 15.5601 15.5595C15.2663 15.8532 14.9129 16.0001 14.5001 16.0001H5.49514Z"
                  fill="#1B75BC"
                />
              </svg>
              <button onClick={downloadAsPDF} className="">
                Download
              </button>
            </div>

            <div>
              <div className="flex items-center space-x-3">
                <p className="text-[#1A1C1D] text-opacity-70">
                  Does this answer meet your needs?
                </p>
                <svg
                  className={`w-6 h-6 cursor-pointer ${
                    selected === "like"
                      ? "text-blue-500"
                      : "text-gray-600 opacity-40"
                  }`}
                  onClick={() =>
                    setSelected(selected === "like" ? null : "like")
                  }
                  viewBox="0 0 18 18"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M15.7504 6.28127C16.0879 6.28127 16.3973 6.4219 16.6785 6.70315C16.9598 6.9844 17.1004 7.29377 17.1004 7.63127V8.70002C17.1004 8.80002 17.091 8.89377 17.0723 8.98127C17.0535 9.06877 17.0254 9.15002 16.9879 9.22502L14.7566 14.4563C14.6441 14.7188 14.4348 14.925 14.1285 15.075C13.8223 15.225 13.5254 15.3 13.2379 15.3L4.95039 15.2813V6.28127L9.33789 1.89377C9.57539 1.65627 9.84727 1.50315 10.1535 1.4344C10.4598 1.36565 10.7348 1.40002 10.9785 1.53752C11.2223 1.67502 11.3785 1.8969 11.4473 2.20315C11.516 2.5094 11.5129 2.84377 11.4379 3.20627L10.8004 6.28127H15.7504ZM6.30039 6.84377V13.9313H13.5004L15.7504 8.70002V7.63127H9.15039L10.0691 3.09377L6.30039 6.84377ZM2.25039 15.2813C1.86289 15.2813 1.54102 15.1491 1.28477 14.8847C1.02852 14.6203 0.900391 14.3025 0.900391 13.9313V7.63127C0.900391 7.26002 1.02852 6.94221 1.28477 6.67784C1.54102 6.41346 1.86289 6.28127 2.25039 6.28127H4.95039V7.63127H2.25039V13.9313H4.95039V15.2813H2.25039Z"
                    fill="currentColor"
                    fillOpacity="0.4"
                  />
                </svg>
                <svg
                  className={`w-6 h-6 cursor-pointer ${
                    selected === "dislike"
                      ? "text-blue-500"
                      : "text-gray-600 opacity-40"
                  }`}
                  onClick={() => handleDislikeClick()}
                  viewBox="0 0 18 18"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M2.25039 11.7C1.91289 11.7 1.60352 11.5594 1.32227 11.2781C1.04102 10.9969 0.900391 10.6875 0.900391 10.35V9.28127C0.900391 9.18127 0.909766 9.08752 0.928516 9.00002C0.947266 8.91252 0.975391 8.83127 1.01289 8.75627L3.24414 3.52502C3.35664 3.26252 3.56602 3.05627 3.87227 2.90627C4.17852 2.75627 4.47539 2.68127 4.76289 2.68127L13.0504 2.70002V11.7L8.66289 16.0875C8.42539 16.325 8.15352 16.4781 7.84727 16.5469C7.54102 16.6156 7.26602 16.5813 7.02227 16.4438C6.77852 16.3063 6.62227 16.0844 6.55352 15.7781C6.48477 15.4719 6.48789 15.1375 6.56289 14.775L7.20039 11.7H2.25039ZM11.7004 11.1375V4.05002H4.50039L2.25039 9.28127V10.35H8.85039L7.93164 14.8875L11.7004 11.1375ZM15.7504 2.70002C16.1379 2.70002 16.4598 2.83221 16.716 3.09659C16.9723 3.36096 17.1004 3.67877 17.1004 4.05002V10.35C17.1004 10.7213 16.9723 11.0391 16.716 11.3035C16.4598 11.5678 16.1379 11.7 15.7504 11.7H13.0504V10.35H15.7504V4.05002H13.0504V2.70002H15.7504Z"
                    fill="currentColor"
                    fillOpacity="0.4"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default Component;
