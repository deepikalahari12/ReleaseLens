
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from github_integration import fetch_workflow_runs


from release_traceability import (
    save_workflow_runs,
    get_workflows_for_commit
)
from release_health import assess_release_health
# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DB_PATH = Path(__file__).with_name("releaselens.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS releases (
                id INTEGER PRIMARY KEY,
                version TEXT UNIQUE NOT NULL,
                commit_sha TEXT NOT NULL,
                build_status TEXT NOT NULL,
                test_status TEXT NOT NULL,
                deployment_status TEXT NOT NULL,
                environment TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM releases"
        ).fetchone()[0]

        if count == 0:
            sample_releases = [
                (
                    "v1.0.0",
                    "a1b2c3d",
                    "Passed",
                    "Passed",
                    "Deployed",
                    "Production",
                    "2026-11-12"
                ),
                (
                    "v1.1.0",
                    "e4f5a6b",
                    "Passed",
                    "Failed",
                    "Not Deployed",
                    "Staging",
                    "2026-11-15"
                ),
                (
                    "v1.2.0",
                    "c7d8e9f",
                    "Running",
                    "Pending",
                    "Not Deployed",
                    "Development",
                    "2026-11-18"
                )
            ]

            conn.executemany("""
                INSERT INTO releases (
                    version,
                    commit_sha,
                    build_status,
                    test_status,
                    deployment_status,
                    environment,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, sample_releases)


# ==========================================
# LOAD RELEASE DATA
# ==========================================

def load_releases():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM releases ORDER BY id DESC",
            conn
        )


# ==========================================
# RELEASE READINESS LOGIC
# ==========================================

def calculate_readiness(release):
    if (
        release["build_status"] == "Failed"
        or release["test_status"] == "Failed"
    ):
        return "Blocked"

    if (
        release["build_status"] == "Passed"
        and release["test_status"] == "Passed"
    ):
        return "Ready"

    return "Pending"


# ==========================================
# STREAMLIT DASHBOARD
# ==========================================

def main():

    st.set_page_config(
        page_title="ReleaseLens",
        page_icon="📊",
        layout="wide"
    )

    initialize_database()

    df = load_releases()

    df["readiness"] = df.apply(
        calculate_readiness,
        axis=1
    )

    # ======================================
    # HEADER
    # ======================================

    st.title("📊 ReleaseLens")

    st.subheader(
        "Software Release Visibility Platform"
    )

        
    st.info(
        "ReleaseLens combines sample release records "
        "stored in SQLite with live GitHub Actions "
        "workflow data. Release readiness is currently "
        "calculated from the sample records."
    )

    

    st.divider()

    # ======================================
    # RELEASE METRICS
    # ======================================

    total_releases = len(df)

    ready_releases = (
        df["readiness"] == "Ready"
    ).sum()

    blocked_releases = (
        df["readiness"] == "Blocked"
    ).sum()

    deployed_releases = (
        df["deployment_status"] == "Deployed"
    ).sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Releases",
        total_releases
    )

    col2.metric(
        "Ready Releases",
        ready_releases
    )

    col3.metric(
        "Blocked Releases",
        blocked_releases
    )

    col4.metric(
        "Deployed Releases",
        deployed_releases
    )

    st.divider()

    # ======================================
    # RELEASE OVERVIEW
    # ======================================

    st.header("Release Overview")

    st.dataframe(
        df[
            [
                "version",
                "commit_sha",
                "build_status",
                "test_status",
                "deployment_status",
                "readiness"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # ======================================
    # READINESS CHART
    # ======================================

    st.header("Release Readiness Distribution")

    readiness_counts = (
        df["readiness"].value_counts()
    )

    st.bar_chart(readiness_counts)

    st.divider()

    # ======================================
    # RELEASE TRACEABILITY
    # ======================================

    st.header("Release Traceability")

    st.subheader("Live Workflow Traceability")

    selected_commit = st.text_input(
        "Enter a GitHub commit SHA",
        value="be820ef"
    )

    if selected_commit:
        matching_runs = get_workflows_for_commit(
            selected_commit.strip()
        )

        if matching_runs:
            st.success(
                f"Found {len(matching_runs)} workflow run(s)"
            )

            st.dataframe(
                pd.DataFrame(matching_runs),
                width="stretch",
                hide_index=True
            )


            st.subheader("Evidence-Based Release Health")

            assessment = assess_release_health(matching_runs)

            st.write("**CI Health:**", assessment["status"])
            st.write("**Assessment Reason:**", assessment["reason"])
            st.write("**Deployment Status:**", assessment["deployment"])

        else:
            st.info(
                "No stored workflow evidence "
                "found for this commit."
            )

    st.divider()

    selected_version = st.selectbox(
        "Select a release",
        df["version"].tolist()
    )

    release = df[
        df["version"] == selected_version
    ].iloc[0]

    st.write(
        "**Release Version:**",
        release["version"]
    )

    st.write(
        "**Source Commit:**",
        release["commit_sha"]
    )

    st.write(
        "**Build Status:**",
        release["build_status"]
    )

    st.write(
        "**Test Status:**",
        release["test_status"]
    )

    st.write(
        "**Deployment Status:**",
        release["deployment_status"]
    )

    st.write(
        "**Environment:**",
        release["environment"]
    )

    st.write(
        "**Last Updated:**",
        release["updated_at"]
    )

    # ======================================
    # RELEASE HEALTH
    # ======================================

    readiness = release["readiness"]

    st.subheader("Release Health Assessment")

    if readiness == "Ready":
        st.success(
            "Release readiness: READY"
        )

    elif readiness == "Blocked":
        st.error(
            "Release readiness: BLOCKED"
        )

    else:
        st.warning(
            "Release readiness: PENDING"
        )

    st.caption(
        "Readiness is calculated from build "
        "and test status. This prototype "
        "does not independently verify "
        "production deployment safety."
    )

    st.divider()

    
    # ======================================
    # LIVE GITHUB ACTIONS MONITORING
    # ======================================

    st.header("Live GitHub Actions Monitoring")

    st.info(
        "Real workflow data retrieved from the "
        "public ReleaseLens GitHub repository."
    )

    if st.button("Refresh GitHub Workflows"):
        st.rerun()

    try:


    
        workflow_runs = fetch_workflow_runs()
        save_workflow_runs(workflow_runs)


        if workflow_runs:
            workflow_df = pd.DataFrame(workflow_runs)

            st.metric(
                "Workflow Runs Retrieved",
                len(workflow_df)
            )

            st.dataframe(
                workflow_df,
                width="stretch",
                hide_index=True,
                column_config={
                    "url": st.column_config.LinkColumn(
                        "GitHub Workflow Link"
                    )
                }
            )

        else:
            st.warning(
                "No GitHub Actions workflow runs found."
            )

    except Exception as error:
        st.error(
            f"Unable to retrieve GitHub Actions data: {error}"
        )

    st.divider()


    st.caption(
        "ReleaseLens | Software Release "
        "Monitoring and Traceability Prototype"
    )


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()
