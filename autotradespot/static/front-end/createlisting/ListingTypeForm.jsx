import React, { useState } from "react";
import LoadIcon from "./LoadIcon";

export default function ListingTypeForm(props) {
    const typeChoices = [//TODO:get from backend
        {"value": "S", "label": "Sale"},
        {"value": "L", "label": "Lease"}
    ]

    const LeasePriceChoices = [
        {"value": "P", "label": "private"},
        {"value": "O", "label": "operational"},
        {"value": "NO", "label": "netto operational"},
        {"value": "F", "label": "financial"},
        {"value": "S", "label": "short"}
    ]

    const SalePriceChoices = [
        {"value": "F", "label": "fixed price"},
        {"value": "N", "label": "negotiable"},
        {"value": "O", "label": "open for bidding"}
    ]

    const [formData, setFormData] = useState({
        type: typeChoices[0].value,
        priceType: "",
        price: 0,
        errors: {},
        loading: false,
    });


    const handleChange = (event) => {
        const { name, value } = event.target;
        setFormData((prevState) => ({ ...prevState, [name]: value }));
    };

    const validateForm = () => {
        const errors = {};

        if (!formData.type) {
            errors.type = "type is required";
        }

        if (!formData.priceType) {
            errors.priceType = "priceType is required";
        }

        if (!formData.price || formData.price < 0) {
            errors.price = "price is required";
        }

        setFormData((prevState) => ({ ...prevState, errors: errors }));
        return Object.keys(errors).length === 0;
    };

    const handleSubmit = (event) => {
        event.preventDefault();

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
            setFormData({
                ...formData,
                loading: false,
            });
        }, 2000);
    };

    return (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <label className="form-control w-full max-w-xs">
                <div className="label">
                    <span className="label-text text-base-content">Type</span>
                </div>
                <select
                    type="select"
                    name="type"
                    value={formData.type}
                    onChange={handleChange}
                    className={`select select-bordered select-sm w-full max-w-xs ${formData.errors.type? "select-error": ""}`}
                >
                    {typeChoices.map((typeChoice) => (
                        <option key={typeChoice.value} value={typeChoice.value}>
                            {typeChoice.label}
                        </option>
                    ))}
                </select>

                {formData.errors.type && (
                    <p className="text-red-500">{formData.errors.type}</p>
                )}
            </label>
            <label className="form-control w-full max-w-xs">
                <div className="label">
                    <span className="label-text text-base-content">Price type</span>
                </div>
                <select
                    type="text"
                    name="priceType"
                    value={formData.priceType}
                    onChange={handleChange}
                    className={`select select-bordered select-sm w-full max-w-xs ${formData.errors.priceType? "select-error": ""}`}
                >
                    {formData.type === "S" ? SalePriceChoices.map((typeChoice) => (
                        <option key={typeChoice.value} value={typeChoice.value}>
                            {typeChoice.label}
                        </option>
                    )) : LeasePriceChoices.map((typeChoice) => (
                        <option key={typeChoice.value} value={typeChoice.value}>
                            {typeChoice.label}
                        </option>
                    ))}
                </select>
                {formData.errors.priceType && (
                    <p className="text-red-500">{formData.errors.priceType}</p>
                )}
            </label>
            <label className="form-control w-full max-w-xs">
                <div className="label">
                    <span className="label-text text-base-content">Price</span>
                </div>
                <span className={`flex flex-row relative items-center gap-2 input input-bordered input-sm w-full max-w-xs ${formData.errors.price? "input-error": ""}`}>
                    <input
                        className="flex-grow"
                        type="number"
                        name="price"
                        value={formData.price}
                        onChange={handleChange}
                    />
                    <span className="absolute right-2 text-gray-400">{formData.type === "S" ? "total" : "per month"}</span>
                </span>
                {formData.errors.price && (
                    <p className="text-red-500">{formData.errors.price}</p>
                )}
            </label>

            <div className="form-control w-full max-w-xs">
                <button
                    type="submit"
                    className="btn btn-primary w-full max-w-xs"
                >
                    {formData.loading ? <LoadIcon /> : "Submit"}
                </button>
            </div>
        </form>
    )

}
