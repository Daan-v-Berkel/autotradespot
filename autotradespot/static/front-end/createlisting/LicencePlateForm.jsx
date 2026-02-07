import React, { useState } from 'react';
import LoadIcon from './LoadIcon';

export default function LicencePlateForm(props) {

    const [formData, setFormData] = useState({
        licenceplate: "",
        errors: {
          licenceplate: "",
        },
        loading: false,
      });

      const handleChange = (event) => {
        const { name, value } = event.target;
        setFormData((prevState) => ({ ...prevState, [name]: value }));
      };

      const validateForm = () => {
        const errors = {};

        if (!formData.licenceplate) {
          errors.licenceplate = "licenceplate is required";
        }

        setFormData((prevState) => ({ ...prevState, errors:errors }));
        return Object.keys(errors).length === 0 ;
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

      const handleSkip = () => {
        props.handleFormPartChange(1)
      }

    return (
        <form className="flex flex-col space-y-4" onSubmit={handleSubmit}>
        <label className="form-control w-full max-w-xs">
          <div className="label">
            <span className="label-text text-base-content">Licenceplate:</span>
          </div>
          <input type="text"
                 name="licenceplate"
                 placeholder="AA-00-BB"
                 value={formData.licenceplate}
                 onChange={handleChange}
                 className={`input input-bordered input-sm w-full max-w-xs ${formData.errors.licenceplate? "input-error": ""}`} />
        </label>
        {formData.errors.licenceplate && <p className="text-error">{formData.errors.licenceplate}</p>}
        <span className="flex flex-row space-x-2">
          <button className="btn btn-primary btn-wide"
                  type="submit"
                  disabled={formData.loading}
                  onClick={handleSubmit}>
            {formData.loading?
            <span className="flex flex-row">loading... <LoadIcon /></span> :
             "continue"}
          </button>
          <button className="btn btn-secondary"
                  type="button"
                  disabled={formData.loading}
                  onClick={handleSkip}>
            skip
          </button>
        </span>
      </form>
    )
}
