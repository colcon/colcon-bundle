import * as core from '@actions/core';
import CloudWatch from 'aws-sdk/clients/cloudwatch';

const cloudwatch = new CloudWatch();

const FAILED_BUILDS_METRIC_NAME = 'FailedBuilds'
const NUM_BUILDS_METRIC_NAME = 'Builds'
const SUCCESS_BUILDS_METRIC_NAME = 'SucceededBuilds'
const PROJECT_DIMENSION = 'ProjectName'
const IS_CRON_JOB_DIMENSION = 'IsCronJob'

function createMetricDatum(metricName, projectName, isCronJob, value) {
  const cronJobString = isCronJob ? 'True' : 'False'
  const metric_datum = { 'MetricName': metricName, 'Value': value, 
    'Dimensions': [ 
      { 'Name': PROJECT_DIMENSION, 'Value': projectName },
      { 'Name': IS_CRON_JOB_DIMENSION, 'Value': cronJobString }
    ] 
  } 
  return metric_datum
}

async function publishMetricData(metricData) {
  try {
    const metricNamespace = core.getInput('namespace');
    console.log(`Publishing metrics ${console.dir(metricData, {depth: false})} under namespace ${metricNamespace}`);
    await cloudwatch.putMetricData({
      Namespace: metricNamespace,
      MetricData: metricData
    }).promise();
    console.log("Successfully published metrics");
  } catch (error) {
    core.setFailed(error.message);
  }
}

async function postBuildStatus() {
  try {
    const buildStatus = core.getInput('status', { required: true });
    const projectName = core.getInput('project-name');
    const validBuildStatusCheck = new RegExp('(success|failure)');
    if (!buildStatus.match(validBuildStatusCheck)) {
      throw new Error(`Invalid build status ${buildStatus} passed to cw-build-status`);
    }
    const isFailedBuild: Boolean = buildStatus === 'failure';

    const metricData = [createMetricDatum(NUM_BUILDS_METRIC_NAME, projectName, false, 1.0)]
    metricData.push(createMetricDatum(FAILED_BUILDS_METRIC_NAME, projectName, false, isFailedBuild ? 1.0 : 0.0))
    metricData.push(createMetricDatum(SUCCESS_BUILDS_METRIC_NAME, projectName, false, isFailedBuild ? 0.0 : 1.0))

    await publishMetricData(metricData);

    console.log("Received build status: ", buildStatus);
  } catch (error) {
    core.setFailed(error.message);
  }
}

async function run() {
  await postBuildStatus();
}

run();
