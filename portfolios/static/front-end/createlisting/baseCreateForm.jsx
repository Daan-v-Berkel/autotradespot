import React, { useState } from "react";
import LicencePlateForm from "./LicencePlateForm";
import ListingTypeForm from "./ListingTypeForm";
import ListingMakeForm from "./ListingMakeForm";

export default function BaseCreateForm() {

    const [activeFormPart, setActiveFormPart] = useState(0);//index of active form part
    const formPartStrings = ["licenceplate", "type", "make", "details", "images"];
    const formComponents = [
        <LicencePlateForm handleFormPartChange={setActiveFormPart}/>,
        <ListingTypeForm handleFormPartChange={setActiveFormPart}/>,
        <ListingMakeForm handleFormPartChange={setActiveFormPart}/>,
    ]

    function getActiveFormPart() {
        return formComponents[activeFormPart];
    };

    return (
        <div className="join flex flex-row my-4 mx-auto min-w-full" role="tablist">
            <ul className="join-item steps steps-vertical overflow-x-hidden bg-base-200 max-h-fit border-2 border-base-300 mb-auto md:w-full max-w-fit px-2 md:pr-8">
                {formPartStrings.map((formPart, index) => (
                    <li key={index}
                        className={`step cursor-pointer ${activeFormPart === index ? "step-primary" : ""}`}
                        onClick={() => setActiveFormPart(index)}>
                        <span className="hidden md:block text-sm text-base-content">{formPart}</span>
                    </li>
                ))}
            </ul>
            <div className="join-item flex flex-col justify-between w-full bg-base-200 p-4 rounded-box border-2 border-l-0 border-base-300">
                <div id="tabcontent">{getActiveFormPart()}</div>
                <div id="adform_actions" className="flex flex-row space-x-4 mt-4">
                    <button className="btn btn-secondary">
                    <span className="ti-eraser"></span> Clear
                    </button>
                    <button className="btn btn-outline btn-secondary">Continue later</button>
                </div>
            </div>
        </ div>
    );

}
