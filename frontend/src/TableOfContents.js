import React from 'react';
import "./css/toc.scss"
import chapters from "./chapters.json"
import {bookState} from "./book/store";

export const TableOfContents = () => {
  const current = bookState.user.pageSlug;
  return (
    <div className="backend bg-dark toc">
      <div className="toc-header">
        <div className="container">
          <h1>futurecoder</h1>
          <p>
            Below are links to different pages in the course.
            You can start anywhere and go in any order,
            and your progress on each page will be recorded. <br/>
            If you're completely new to programming, or you have doubts,
            just start at the beginning and click Next as you finish each page.
          </p>
        </div>
      </div>

      <div className="container toc-container">
        <div className="row">
          <div className="col-md-9" role="main">
            <div className="toc-section">
              <h1 id="toc-toc">
                Table of Contents
              </h1>
              <ol className="toc-ol">
                {chapters.map(chapter =>
                  <li>
                    <h2>{chapter.title}</h2>
                    <ol>
                      {chapter.pages.map(page => {
                        const isCurrent = page.slug === current;
                          return <li>
                            <a href={"#" + page.slug}
                               style={isCurrent ? {
                                 border: '2px solid white',
                                 fontWeight: 'bold',
                                 padding: '5px',
                                 lineHeight: 2
                               } : {}}
                              // May have HTML generated from markdown
                               dangerouslySetInnerHTML={{__html: page.title}}/>
                            {isCurrent && " (current)"}
                          </li>;
                        }
                      )}
                    </ol>
                  </li>
                )}
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
