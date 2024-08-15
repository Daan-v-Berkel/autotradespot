import React, { useState, useEffect } from "react";
import LoadIcon from "./LoadIcon";


export default function ListingMakeForm(props) {
    
    const CARDATA = JSON.parse(document.getElementById('car_context').textContent);
    const CAR_MAKES = CARDATA.car_makes;
    const [CAR_MODELS, setCAR_MODELS] = useState(CARDATA.car_models);
    
    const [formData, setFormData] = useState({
        make: {},
        model: {},
        variant: "",
        errors: {},
        loading: false,
    });

    const handleChange = (event) => {
        const { name, value } = event.target;
        setFormData((prevState) => ({ ...prevState, [name]: value }));
    };

    const validateForm = () => {
        const errors = {};

        if (!formData.make) {
            errors.make = "make is required";
        }

        if (!formData.model) {
            errors.model = "model is required";
        }

        if (!formData.variant) {
            errors.variant = "variant is required";
        }

        setFormData((prevState) => ({ ...prevState, errors: errors }));
        return Object.keys(errors).length === 0;
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        console.log(`formData: ${JSON.stringify(formData)}`)

        setFormData({
            ...formData,
            loading: true,
        });

        if (!validateForm()) {
            setFormData({
                ...formData,
                loading: false,
            });
            return;
        }

        // Simulate form submission delay
        setTimeout(() => {
            console.log(formData);
            setFormData({
                ...formData,
                loading: false,
            });
        }, 2000);
    };

    return (
        <form
            className="flex flex-col space-y-2"
            onSubmit={handleSubmit}
        >
            <div className="form-control w-full">
                <label className="label">
                    <span className="label-text">make</span>
                </label>
                <select
                    name="make"
                    value={formData.make}
                    onChange={handleChange}
                    className="select select-bordered w-full" >

                    {CAR_MAKES.map((make) => (
                        <option key={make.id} value={make}>
                            {make.name}
                        </option>
                    ))}
                </select>
                {formData.errors.make && (
                    <label className="label">
                        <span className="label-text-alt text-error">
                            {formData.errors.make}
                        </span>
                    </label>
                )}
            </div>
            <div className="form-control w-full">
                <label className="label">
                    <span className="label-text">model</span>
                </label>
                <select  type="text"
                    name="model"
                    value={formData.model}
                    onChange={handleChange}
                    className="select select-bordered w-full" >
                        {CAR_MODELS.map((model) => (
                            <option key={model.id} value={model}>
                                {model.name}
                            </option>
                        ))}
                </select>
                {formData.errors.model && (
                    <label className="label">
                        <span className="label-text-alt text-error">
                            {formData.errors.model}
                        </span>
                    </label>
                )}
            </div>
            <div className="form-control w-full">
                <label className="label">
                    <span className="label-text">variant</span>
                </label>
                <input
                    type="text"
                    name="variant"
                    value={formData.variant}
                    onChange={handleChange}
                    className="input input-bordered w-full" />
                {formData.errors.variant && (
                    <label className="label">
                        <span className="label-text-alt text-error">
                            {formData.errors.variant}
                        </span>
                    </label>
                )}
            </div>
            <button
                type="submit"
                className="btn btn-primary btn-wide"
                disabled={formData.loading}
            >
                {formData.loading ? <LoadIcon /> : "Submit"}
            </button>
        </form>
    );
}