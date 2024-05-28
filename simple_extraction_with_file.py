import streamlit as st
import pandas as pd
import re
import io

def extract_quantifications(file, search_terms):
    df = pd.read_excel(file)
    quantifications = {}
    extracted_data = []

    for term, keywords in search_terms.items():
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(',')]
        else:
            keywords = [k.strip() for k in keywords]
        pattern = r'|'.join(map(re.escape, keywords))
        df['count'] = df['Sound Bite Text'].str.contains(pattern, case=False).astype(int)
        quantifications[term] = df['count'].sum()

        extracted_rows = df[df['count'] == 1][['Post ID','Sound Bite Text']].reset_index(drop=True)
        extracted_rows['Extractions'] = term
        extracted_data.extend(extracted_rows.to_dict('records'))

    return quantifications, extracted_data

def main():
    st.title("113 Quantification Tool")

    file = st.file_uploader("Upload an Excel file", type=["xlsx"])

    if file is not None:
        search_terms = {}
        num_terms = st.number_input("Enter the number of terms to search for", min_value=1, step=1)

        for i in range(num_terms):
            term = st.text_input(f"Enter term {i+1}", key=f"term_{i+1}")
            keywords = st.text_area(f"Enter keywords for '{term}' (comma-separated)", key=f"keywords_{i+1}")
            if keywords:
                keywords = [k.strip() for k in keywords.split(",")]
                search_terms[term] = keywords

        if st.button("Extract Quantifications"):
            quantifications, extracted_data = extract_quantifications(file, search_terms)
            st.write("Quantifications:")
            for term, count in quantifications.items():
                st.write(f"{term}: {count}")

            output_df = pd.DataFrame(extracted_data)
            output_file = "output_file.xlsx"

            # Create a BytesIO object to store the Excel data
            xlsx_buffer = io.BytesIO()

            # Save the DataFrame to the BytesIO object
            with pd.ExcelWriter(xlsx_buffer) as writer:
                output_df.to_excel(writer, index=False, sheet_name='Sheet1')

            # Create a download link for the Excel file
            st.download_button(
                label="Download Output File",
                data=xlsx_buffer.getvalue(),
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()