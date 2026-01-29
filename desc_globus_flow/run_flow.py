from globus_sdk import SpecificFlowClient, UserApp


__all__ = ["run_flow"]


def run_flow(flow_input, flow_id, app_name="lsst-desc-flow-app",
             label="lsst-desc-test"):
    # Public Globus thick client for authentication
    AUTH_CLIENT_ID = "f818e8c5-61ba-4f70-8237-a8e69f266ae7"

    # Create authenticated Flows client. NOTE: This can be changed to
    # use client's secrets to avoid having to authenticate
    specific_flow_client = SpecificFlowClient(
        flow_id=flow_id,
        app=UserApp(
            client_id=AUTH_CLIENT_ID,
            app_name=app_name
        )
    )

    # Start the flow
    run = specific_flow_client.run_flow(
        body=flow_input,
        label=label
    )

    # Collect the run UUID
    run_id = run["run_id"]
    print(f"\nRun ID: {run_id}")
    print(f"Check status at: https://app.globus.org/runs/{run_id}/logs\n")
