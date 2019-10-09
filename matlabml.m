dbfile = fullfile(pwd, "results.db");
conn = sqlite(dbfile, "readonly");

results = fetch(conn, "SELECT * FROM result");