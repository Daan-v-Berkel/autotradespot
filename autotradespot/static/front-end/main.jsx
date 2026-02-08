import React from 'react';
import ReactDOM from 'react-dom/client';
import Try from './test.jsx';
// import BaseCreateForm from './createlisting/baseCreateForm.jsx';
import ListingFormContainer from './createlisting/ListingFormContainer.jsx';

if (document.getElementById('ditisjantje')) {
    ReactDOM.createRoot(document.getElementById('ditisjantje')).render(<Try />)
  }


if (document.getElementById("create-listing-base")) {
    ReactDOM.createRoot(document.getElementById("create-listing-base")).render(
        // <BaseCreateForm />
				<ListingFormContainer />
    );
}
