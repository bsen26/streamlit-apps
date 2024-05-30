import streamlit as st
import pandas as pd
import re
import io

def extract_quantifications(data_file, terms_file):
    data_df = pd.read_excel(data_file)
    terms_df = pd.read_excel(terms_file)

    quantifications = {}
    extracted_data = []

    for _, row in terms_df.iterrows():
        term = row['Terms']
        include_terms = []
        exclude_terms = []

        for phrase in row['Include Terms'].split(','):
            if '~' in phrase:
                phrase, slop = phrase.split('~')
                slop = int(slop)
                pattern = r'\b{}\b(?:\W+\w+){0,SLOP_PLACEHOLDER}?\b(?=.*?\b\w*?(?:\W+\w+){0,SLOP_PLACEHOLDER}?\b)'
                pattern = re.sub(r'SLOP_PLACEHOLDER', str(slop), pattern)
            else:
                pattern = r'\b{}\b'.format(re.escape(phrase))  # Match exact phrase

            include_terms.append(pattern)

        if pd.notnull(row['Exclude Terms']):
            for phrase in row['Exclude Terms'].split(','):
                if '~' in phrase:
                    phrase, slop = phrase.split('~')
                    slop = int(slop)
                    pattern = r'\b{}\b(?:\W+\w+){0,SLOP_PLACEHOLDER}?\b(?=.*?\b\w*?(?:\W+\w+){0,SLOP_PLACEHOLDER}?\b)'
                    pattern = re.sub(r'SLOP_PLACEHOLDER', str(slop), pattern)
                else:
                    pattern = r'\b{}\b'.format(re.escape(phrase))  # Match exact phrase

                exclude_terms.append(pattern)

        include_pattern = r'|'.join(include_terms)
        data_df['include_count'] = data_df['Sound Bite Text'].str.contains(include_pattern, case=False, regex=True).astype(int)

        if exclude_terms:
            exclude_pattern = r'|'.join(exclude_terms)
            data_df['exclude_count'] = data_df['Sound Bite Text'].str.contains(exclude_pattern, case=False, regex=True).astype(int)
            data_df['count'] = data_df['include_count'] - data_df['exclude_count']
        else:
            data_df['count'] = data_df['include_count']

        quantifications[term] = data_df['count'].sum()
        extracted_rows = data_df[data_df['count'] == 1][['Post ID', 'Sound Bite Text']].reset_index(drop=True)
        extracted_rows['Extractions'] = term
        extracted_data.extend(extracted_rows.to_dict('records'))

    return quantifications, extracted_data

def main():
    st.title("113 Quantification Tool")
    data_file = st.file_uploader("Upload the data file", type=["xlsx"])
    terms_file = st.file_uploader("Upload the terms file", type=["xlsx"])

    if data_file is not None and terms_file is not None:
        if st.button("Extract Quantifications"):
            quantifications, extracted_data = extract_quantifications(data_file, terms_file)
            st.write("Quantifications:")
            for term, count in quantifications.items():
                st.write(f"{term}: {count}")

            output_df = pd.DataFrame(extracted_data)
            output_file = "output_file.xlsx"
            xlsx_buffer = io.BytesIO()
            with pd.ExcelWriter(xlsx_buffer) as writer:
                output_df.to_excel(writer, index=False, sheet_name='Sheet1')

            st.download_button(
                label="Download Output File",
                data=xlsx_buffer.getvalue(),
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()