from flask import Flask, render_template_string
import pandas as pd
import argparse

from minio_utils import * 

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run Flask app to display MinIO metadata.')
    parser.add_argument('--bucket_name', type=str, required=True, help='The name of the MinIO bucket.')
    parser.add_argument('--credentials', type=str, required=True, help='Path to the MinIO credentials file.')
    
    args = parser.parse_args()
    return args.bucket_name, args.credentials

from flask import Flask, render_template_string
import pandas as pd
def render_interactive_table(df):
    html_table = df.to_html(classes='table table-striped table-bordered', index=False, border=0)
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Metadata Table with Column Filters</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/dataTables.bootstrap4.min.css">
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/buttons/1.6.2/css/buttons.bootstrap4.min.css">
        <script src="https://code.jquery.com/jquery-3.5.1.js"></script>
        <script src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
        <script src="https://cdn.datatables.net/1.10.21/js/dataTables.bootstrap4.min.js"></script>
        <script src="https://cdn.datatables.net/buttons/1.6.2/js/dataTables.buttons.min.js"></script>
        <script src="https://cdn.datatables.net/buttons/1.6.2/js/buttons.bootstrap4.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/pdfmake.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/vfs_fonts.js"></script>
        <script src="https://cdn.datatables.net/buttons/1.6.2/js/buttons.html5.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    </head>
    <body>
        <table id="metadataTable" class="table table-striped table-bordered" style="width:100%">
            <thead>
                <tr>
                    {% for column in df.columns %}
                    <th>{{ column }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in df.itertuples() %}
                <tr>
                    {% for cell in row[1:] %}
                    <td>{{ cell }}</td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <script>
        $(document).ready(function() {
            var table = $('#metadataTable').DataTable({
                dom: 'Bfrtip',
                buttons: [
                    { extend: 'copy', className: 'btn btn-primary' },
                    { extend: 'csv', className: 'btn btn-primary' },
                    { extend: 'excel', className: 'btn btn-primary' },
                    { extend: 'pdf', className: 'btn btn-primary' }
                ],
                "pagingType": "full_numbers",
                "lengthChange": false,
                "searching": true,
                "ordering": true,
                "info": true,
                "autoWidth": false,
                "responsive": true,
            });
        });
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, df=df)

app = Flask(__name__)

@app.route('/')
def index():
    # bucket_name = "dev"
    # minio_credentials = "credentials_python_minio.json"
    metadatadf = extract_metadata_of_all_objects(bucket_name = bucket_name, 
                                                 minio_credentials = minio_credentials, 
                                                 simplified = True)
    return render_interactive_table(metadatadf)

if __name__ == '__main__':
    bucket_name, minio_credentials = parse_arguments()
    app.run(debug=True)