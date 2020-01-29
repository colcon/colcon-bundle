#!/usr/bin/env node

const sgMail = require('@sendgrid/mail');
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

const msg = {
  to: process.env.AWS_ONCALL_PAGE_EMAIL,
  from: process.env.AWS_ONCALL_EMAIL,
  subject: `A workflow in ${process.env.GITHUB_REPOSITORY} is failing`,
  text: `The workflow ${process.env.GITHUB_WORKFLOW} in ${process.env.GITHUB_REPOSITORY} is failing.`,
  html: `<p>\
  The workflow ${process.env.GITHUB_WORKFLOW} in \
  <a href="https://www.github.com/${process.env.GITHUB_REPOSITORY}">${process.env.GITHUB_REPOSITORY}</a> is failing.\
  </p>`,
};

sgMail
  .send(msg)
  .then(() => console.log('Mail sent successfully'))
  .catch(error => console.error(error.toString()));